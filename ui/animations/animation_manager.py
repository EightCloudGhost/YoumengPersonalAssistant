# -*- coding: utf-8 -*-
"""
动画管理器 - 提供统一的动画效果管理
"""

from PyQt5.QtCore import (
    QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup,
    QEasingCurve, QPoint, QRect, pyqtSignal, QObject
)
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect


class AnimationManager(QObject):
    """动画管理器，提供各种动画效果的统一接口"""
    
    # 动画完成信号
    animation_finished = pyqtSignal()
    
    # 预设动画时长（毫秒）
    DURATION_FAST = 150
    DURATION_NORMAL = 250
    DURATION_SLOW = 350
    
    # 预设缓动曲线
    EASING_DEFAULT = QEasingCurve.OutCubic
    EASING_BOUNCE = QEasingCurve.OutBack
    EASING_SMOOTH = QEasingCurve.OutQuart
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_animations = []
    
    def fade_in(self, widget: QWidget, duration: int = None, 
                callback=None) -> QPropertyAnimation:
        """
        淡入动画
        
        Args:
            widget: 目标控件
            duration: 动画时长（毫秒）
            callback: 动画完成回调
        """
        if duration is None:
            duration = self.DURATION_NORMAL
        
        # 确保控件有透明度效果
        effect = self._ensure_opacity_effect(widget)
        effect.setOpacity(0.0)
        widget.show()
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(self.EASING_DEFAULT)
        
        if callback:
            animation.finished.connect(callback)
        
        self._track_animation(animation)
        animation.start()
        return animation
    
    def fade_out(self, widget: QWidget, duration: int = None,
                 hide_on_finish: bool = True, callback=None) -> QPropertyAnimation:
        """
        淡出动画
        
        Args:
            widget: 目标控件
            duration: 动画时长（毫秒）
            hide_on_finish: 动画结束后是否隐藏控件
            callback: 动画完成回调
        """
        if duration is None:
            duration = self.DURATION_NORMAL
        
        effect = self._ensure_opacity_effect(widget)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(self.EASING_DEFAULT)
        
        def on_finished():
            if hide_on_finish:
                widget.hide()
            if callback:
                callback()
        
        animation.finished.connect(on_finished)
        self._track_animation(animation)
        animation.start()
        return animation
    
    def slide_in(self, widget: QWidget, direction: str = 'left',
                 distance: int = 100, duration: int = None,
                 callback=None) -> QPropertyAnimation:
        """
        滑入动画
        
        Args:
            widget: 目标控件
            direction: 滑入方向 ('left', 'right', 'up', 'down')
            distance: 滑动距离（像素）
            duration: 动画时长（毫秒）
            callback: 动画完成回调
        """
        if duration is None:
            duration = self.DURATION_SLOW
        
        target_pos = widget.pos()
        
        # 计算起始位置
        if direction == 'left':
            start_pos = QPoint(target_pos.x() + distance, target_pos.y())
        elif direction == 'right':
            start_pos = QPoint(target_pos.x() - distance, target_pos.y())
        elif direction == 'up':
            start_pos = QPoint(target_pos.x(), target_pos.y() + distance)
        elif direction == 'down':
            start_pos = QPoint(target_pos.x(), target_pos.y() - distance)
        else:
            start_pos = target_pos
        
        widget.move(start_pos)
        widget.show()
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(target_pos)
        animation.setEasingCurve(self.EASING_SMOOTH)
        
        if callback:
            animation.finished.connect(callback)
        
        self._track_animation(animation)
        animation.start()
        return animation
    
    def slide_out(self, widget: QWidget, direction: str = 'right',
                  distance: int = 100, duration: int = None,
                  hide_on_finish: bool = True, callback=None) -> QPropertyAnimation:
        """
        滑出动画
        
        Args:
            widget: 目标控件
            direction: 滑出方向 ('left', 'right', 'up', 'down')
            distance: 滑动距离（像素）
            duration: 动画时长（毫秒）
            hide_on_finish: 动画结束后是否隐藏控件
            callback: 动画完成回调
        """
        if duration is None:
            duration = self.DURATION_NORMAL
        
        start_pos = widget.pos()
        
        # 计算结束位置
        if direction == 'left':
            end_pos = QPoint(start_pos.x() - distance, start_pos.y())
        elif direction == 'right':
            end_pos = QPoint(start_pos.x() + distance, start_pos.y())
        elif direction == 'up':
            end_pos = QPoint(start_pos.x(), start_pos.y() - distance)
        elif direction == 'down':
            end_pos = QPoint(start_pos.x(), start_pos.y() + distance)
        else:
            end_pos = start_pos
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(self.EASING_DEFAULT)
        
        def on_finished():
            if hide_on_finish:
                widget.hide()
            widget.move(start_pos)  # 恢复原位置
            if callback:
                callback()
        
        animation.finished.connect(on_finished)
        self._track_animation(animation)
        animation.start()
        return animation
    
    def expand_width(self, widget: QWidget, target_width: int,
                     duration: int = None, callback=None) -> QPropertyAnimation:
        """
        宽度展开动画
        
        Args:
            widget: 目标控件
            target_width: 目标宽度
            duration: 动画时长（毫秒）
            callback: 动画完成回调
        """
        if duration is None:
            duration = self.DURATION_SLOW
        
        animation = QPropertyAnimation(widget, b"maximumWidth")
        animation.setDuration(duration)
        animation.setStartValue(widget.width())
        animation.setEndValue(target_width)
        animation.setEasingCurve(self.EASING_DEFAULT)
        
        if callback:
            animation.finished.connect(callback)
        
        self._track_animation(animation)
        animation.start()
        return animation
    
    def collapse_width(self, widget: QWidget, duration: int = None,
                       callback=None) -> QPropertyAnimation:
        """
        宽度收起动画
        
        Args:
            widget: 目标控件
            duration: 动画时长（毫秒）
            callback: 动画完成回调
        """
        if duration is None:
            duration = self.DURATION_SLOW
        
        animation = QPropertyAnimation(widget, b"maximumWidth")
        animation.setDuration(duration)
        animation.setStartValue(widget.width())
        animation.setEndValue(0)
        animation.setEasingCurve(self.EASING_DEFAULT)
        
        if callback:
            animation.finished.connect(callback)
        
        self._track_animation(animation)
        animation.start()
        return animation
    
    def fade_switch(self, widget_out: QWidget, widget_in: QWidget,
                    duration: int = None, callback=None) -> QSequentialAnimationGroup:
        """
        淡入淡出切换动画（先淡出再淡入）
        
        Args:
            widget_out: 要淡出的控件
            widget_in: 要淡入的控件
            duration: 总动画时长（毫秒）
            callback: 动画完成回调
        """
        if duration is None:
            duration = self.DURATION_NORMAL
        
        half_duration = duration // 2
        
        # 确保透明度效果
        effect_out = self._ensure_opacity_effect(widget_out)
        effect_in = self._ensure_opacity_effect(widget_in)
        effect_in.setOpacity(0.0)
        
        # 淡出动画
        fade_out_anim = QPropertyAnimation(effect_out, b"opacity")
        fade_out_anim.setDuration(half_duration)
        fade_out_anim.setStartValue(1.0)
        fade_out_anim.setEndValue(0.0)
        fade_out_anim.setEasingCurve(self.EASING_DEFAULT)
        
        # 淡入动画
        fade_in_anim = QPropertyAnimation(effect_in, b"opacity")
        fade_in_anim.setDuration(half_duration)
        fade_in_anim.setStartValue(0.0)
        fade_in_anim.setEndValue(1.0)
        fade_in_anim.setEasingCurve(self.EASING_DEFAULT)
        
        # 顺序动画组
        group = QSequentialAnimationGroup()
        group.addAnimation(fade_out_anim)
        group.addAnimation(fade_in_anim)
        
        def on_fade_out_finished():
            widget_out.hide()
            widget_in.show()
        
        fade_out_anim.finished.connect(on_fade_out_finished)
        
        if callback:
            group.finished.connect(callback)
        
        self._track_animation(group)
        group.start()
        return group
    
    def parallel_fade_slide(self, widget: QWidget, fade_in: bool = True,
                           direction: str = 'left', distance: int = 50,
                           duration: int = None, callback=None) -> QParallelAnimationGroup:
        """
        并行淡入/淡出+滑动动画
        
        Args:
            widget: 目标控件
            fade_in: True为淡入滑入，False为淡出滑出
            direction: 滑动方向
            distance: 滑动距离
            duration: 动画时长
            callback: 动画完成回调
        """
        if duration is None:
            duration = self.DURATION_SLOW
        
        effect = self._ensure_opacity_effect(widget)
        target_pos = widget.pos()
        
        if fade_in:
            # 淡入滑入
            effect.setOpacity(0.0)
            if direction == 'left':
                start_pos = QPoint(target_pos.x() + distance, target_pos.y())
            elif direction == 'right':
                start_pos = QPoint(target_pos.x() - distance, target_pos.y())
            else:
                start_pos = target_pos
            
            widget.move(start_pos)
            widget.show()
            
            opacity_start, opacity_end = 0.0, 1.0
            pos_start, pos_end = start_pos, target_pos
        else:
            # 淡出滑出
            if direction == 'left':
                end_pos = QPoint(target_pos.x() - distance, target_pos.y())
            elif direction == 'right':
                end_pos = QPoint(target_pos.x() + distance, target_pos.y())
            else:
                end_pos = target_pos
            
            opacity_start, opacity_end = 1.0, 0.0
            pos_start, pos_end = target_pos, end_pos
        
        # 透明度动画
        fade_anim = QPropertyAnimation(effect, b"opacity")
        fade_anim.setDuration(duration)
        fade_anim.setStartValue(opacity_start)
        fade_anim.setEndValue(opacity_end)
        fade_anim.setEasingCurve(self.EASING_DEFAULT)
        
        # 位置动画
        pos_anim = QPropertyAnimation(widget, b"pos")
        pos_anim.setDuration(duration)
        pos_anim.setStartValue(pos_start)
        pos_anim.setEndValue(pos_end)
        pos_anim.setEasingCurve(self.EASING_SMOOTH)
        
        # 并行动画组
        group = QParallelAnimationGroup()
        group.addAnimation(fade_anim)
        group.addAnimation(pos_anim)
        
        def on_finished():
            if not fade_in:
                widget.hide()
                widget.move(target_pos)
            if callback:
                callback()
        
        group.finished.connect(on_finished)
        self._track_animation(group)
        group.start()
        return group
    
    def _ensure_opacity_effect(self, widget: QWidget) -> QGraphicsOpacityEffect:
        """确保控件有透明度效果"""
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
        return effect
    
    def _track_animation(self, animation):
        """跟踪动画，动画结束后自动清理"""
        self._active_animations.append(animation)
        animation.finished.connect(lambda: self._remove_animation(animation))
    
    def _remove_animation(self, animation):
        """移除已完成的动画"""
        if animation in self._active_animations:
            self._active_animations.remove(animation)
    
    def stop_all(self):
        """停止所有正在进行的动画"""
        for animation in self._active_animations[:]:
            animation.stop()
        self._active_animations.clear()


# 全局动画管理器实例
animation_manager = AnimationManager()
