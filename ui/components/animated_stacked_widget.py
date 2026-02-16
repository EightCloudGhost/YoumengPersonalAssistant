# -*- coding: utf-8 -*-
"""
带动画效果的QStackedWidget
支持页面切换时的淡入淡出和滑动动画
"""

from PyQt5.QtCore import (
    QPropertyAnimation, QParallelAnimationGroup, QEasingCurve,
    QPoint, pyqtSignal, QTimer
)
from PyQt5.QtWidgets import QStackedWidget, QGraphicsOpacityEffect


class AnimatedStackedWidget(QStackedWidget):
    """带动画效果的堆叠窗口组件"""
    
    # 页面切换完成信号
    page_changed = pyqtSignal(int)
    
    # 动画类型
    ANIMATION_FADE = 'fade'
    ANIMATION_SLIDE_LEFT = 'slide_left'
    ANIMATION_SLIDE_RIGHT = 'slide_right'
    ANIMATION_NONE = 'none'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 动画配置
        self._animation_duration = 250  # 毫秒
        self._animation_type = self.ANIMATION_FADE
        self._is_animating = False
        self._pending_index = None
        
        # 缓动曲线
        self._easing_curve = QEasingCurve.OutCubic
    
    def set_animation_duration(self, duration: int):
        """设置动画时长"""
        self._animation_duration = duration
    
    def set_animation_type(self, animation_type: str):
        """设置动画类型"""
        self._animation_type = animation_type
    
    def set_easing_curve(self, curve: QEasingCurve):
        """设置缓动曲线"""
        self._easing_curve = curve
    
    def setCurrentIndex(self, index: int):
        """重写切换页面方法，添加动画效果"""
        if index == self.currentIndex():
            return
        
        if index < 0 or index >= self.count():
            return
        
        # 如果正在动画中，记录待切换的索引
        if self._is_animating:
            self._pending_index = index
            return
        
        if self._animation_type == self.ANIMATION_NONE:
            super().setCurrentIndex(index)
            self.page_changed.emit(index)
        elif self._animation_type == self.ANIMATION_FADE:
            self._fade_switch(index)
        elif self._animation_type in (self.ANIMATION_SLIDE_LEFT, self.ANIMATION_SLIDE_RIGHT):
            self._slide_switch(index)
        else:
            super().setCurrentIndex(index)
            self.page_changed.emit(index)
    
    def setCurrentWidget(self, widget):
        """重写切换页面方法"""
        index = self.indexOf(widget)
        if index >= 0:
            self.setCurrentIndex(index)
    
    def _fade_switch(self, new_index: int):
        """淡入淡出切换动画"""
        self._is_animating = True
        
        current_widget = self.currentWidget()
        new_widget = self.widget(new_index)
        
        if not current_widget or not new_widget:
            super().setCurrentIndex(new_index)
            self._is_animating = False
            self.page_changed.emit(new_index)
            return
        
        # 为当前页面创建透明度效果
        current_effect = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(current_effect)
        current_effect.setOpacity(1.0)
        
        # 为新页面创建透明度效果
        new_effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(new_effect)
        new_effect.setOpacity(0.0)
        
        # 淡出当前页面
        fade_out = QPropertyAnimation(current_effect, b"opacity")
        fade_out.setDuration(self._animation_duration // 2)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(self._easing_curve)
        
        # 淡入新页面
        fade_in = QPropertyAnimation(new_effect, b"opacity")
        fade_in.setDuration(self._animation_duration // 2)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(self._easing_curve)
        
        def on_fade_out_finished():
            super(AnimatedStackedWidget, self).setCurrentIndex(new_index)
            fade_in.start()
        
        def on_fade_in_finished():
            # 清理透明度效果
            current_widget.setGraphicsEffect(None)
            new_widget.setGraphicsEffect(None)
            self._is_animating = False
            self.page_changed.emit(new_index)
            self._check_pending()
        
        fade_out.finished.connect(on_fade_out_finished)
        fade_in.finished.connect(on_fade_in_finished)
        
        fade_out.start()
    
    def _slide_switch(self, new_index: int):
        """滑动切换动画"""
        self._is_animating = True
        
        current_widget = self.currentWidget()
        new_widget = self.widget(new_index)
        
        if not current_widget or not new_widget:
            super().setCurrentIndex(new_index)
            self._is_animating = False
            self.page_changed.emit(new_index)
            return
        
        # 计算滑动方向
        width = self.width()
        if self._animation_type == self.ANIMATION_SLIDE_LEFT:
            # 新页面从右侧滑入
            direction = -1
        else:
            # 新页面从左侧滑入
            direction = 1
        
        # 也可以根据索引自动判断方向
        if new_index > self.currentIndex():
            direction = -1  # 向左滑
        else:
            direction = 1   # 向右滑
        
        # 保存原始位置
        current_pos = current_widget.pos()
        new_start_pos = QPoint(current_pos.x() - direction * width, current_pos.y())
        new_end_pos = current_pos
        current_end_pos = QPoint(current_pos.x() + direction * width, current_pos.y())
        
        # 准备新页面
        new_widget.move(new_start_pos)
        new_widget.show()
        new_widget.raise_()
        
        # 当前页面滑出动画
        current_anim = QPropertyAnimation(current_widget, b"pos")
        current_anim.setDuration(self._animation_duration)
        current_anim.setStartValue(current_pos)
        current_anim.setEndValue(current_end_pos)
        current_anim.setEasingCurve(self._easing_curve)
        
        # 新页面滑入动画
        new_anim = QPropertyAnimation(new_widget, b"pos")
        new_anim.setDuration(self._animation_duration)
        new_anim.setStartValue(new_start_pos)
        new_anim.setEndValue(new_end_pos)
        new_anim.setEasingCurve(self._easing_curve)
        
        # 并行动画组
        group = QParallelAnimationGroup(self)
        group.addAnimation(current_anim)
        group.addAnimation(new_anim)
        
        def on_finished():
            super(AnimatedStackedWidget, self).setCurrentIndex(new_index)
            current_widget.move(current_pos)
            new_widget.move(new_end_pos)
            self._is_animating = False
            self.page_changed.emit(new_index)
            self._check_pending()
        
        group.finished.connect(on_finished)
        group.start()
    
    def _check_pending(self):
        """检查是否有待处理的页面切换"""
        if self._pending_index is not None:
            pending = self._pending_index
            self._pending_index = None
            QTimer.singleShot(50, lambda: self.setCurrentIndex(pending))
