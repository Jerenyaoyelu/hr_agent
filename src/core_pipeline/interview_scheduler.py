 import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import openai
import json

@dataclass
class Interviewer:
    name: str
    email: str
    expertise: List[str]
    available_slots: List[Dict[str, datetime]]  # 每个slot包含start和end时间

@dataclass
class Candidate:
    name: str
    email: str
    phone: str
    preferred_slots: Optional[List[Dict[str, datetime]]] = None

@dataclass
class Interview:
    candidate: Candidate
    interviewers: List[Interviewer]
    start_time: datetime
    end_time: datetime
    location: str  # 可以是会议室或在线会议链接
    status: str  # scheduled, completed, cancelled
    feedback: Optional[str] = None

class InterviewScheduler:
    def __init__(self, openai_api_key: str):
        """
        初始化面试调度器
        
        Args:
            openai_api_key: OpenAI API密钥
        """
        self.logger = logging.getLogger(__name__)
        self.interviews = []
        openai.api_key = openai_api_key
        
    def _find_common_slots(self, interviewers: List[Interviewer], 
                          candidate: Optional[Candidate] = None) -> List[Dict[str, datetime]]:
        """找到所有参与者的共同可用时间段"""
        # 获取所有面试官的可用时间段
        all_slots = []
        for interviewer in interviewers:
            all_slots.extend(interviewer.available_slots)
            
        # 如果候选人有偏好时间，也考虑进去
        if candidate and candidate.preferred_slots:
            all_slots.extend(candidate.preferred_slots)
            
        # 找出重叠的时间段
        common_slots = []
        for slot in all_slots:
            overlapping = True
            for interviewer in interviewers:
                if not any(
                    self._slots_overlap(slot, interviewer_slot)
                    for interviewer_slot in interviewer.available_slots
                ):
                    overlapping = False
                    break
                    
            if overlapping:
                if not candidate or not candidate.preferred_slots or any(
                    self._slots_overlap(slot, candidate_slot)
                    for candidate_slot in candidate.preferred_slots
                ):
                    common_slots.append(slot)
                    
        return common_slots
        
    def _slots_overlap(self, slot1: Dict[str, datetime], 
                      slot2: Dict[str, datetime]) -> bool:
        """检查两个时间段是否重叠"""
        return (slot1['start'] < slot2['end'] and 
                slot2['start'] < slot1['end'])
                
    def _select_best_slot(self, available_slots: List[Dict[str, datetime]], 
                         duration: timedelta) -> Optional[Dict[str, datetime]]:
        """选择最佳面试时间段"""
        if not available_slots:
            return None
            
        # 优先选择工作日的上午时间段
        for slot in available_slots:
            start = slot['start']
            end = start + duration
            
            if (end <= slot['end'] and  # 确保时间段足够长
                start.weekday() < 5 and  # 工作日
                9 <= start.hour < 12):   # 上午
                return {'start': start, 'end': end}
                
        # 如果没有理想的时间段，选择第一个可用的时间段
        for slot in available_slots:
            start = slot['start']
            end = start + duration
            
            if end <= slot['end']:
                return {'start': start, 'end': end}
                
        return None
        
    def _generate_meeting_link(self) -> str:
        """生成在线会议链接"""
        # 这里应该集成实际的会议系统API
        # 示例实现
        return "https://meet.example.com/" + datetime.now().strftime("%Y%m%d%H%M%S")
        
    def _notify_participants(self, interview: Interview):
        """通知所有参与者面试安排"""
        # 这里应该集成实际的邮件系统
        # 示例实现
        self.logger.info(f"已安排面试：{interview.candidate.name}")
        self.logger.info(f"时间：{interview.start_time} - {interview.end_time}")
        self.logger.info(f"地点：{interview.location}")
        self.logger.info("已通知所有参与者")
        
    def schedule_interview(self, candidate: Candidate, 
                         interviewers: List[Interviewer], 
                         duration: timedelta = timedelta(hours=1),
                         is_online: bool = True) -> Optional[Interview]:
        """
        安排面试
        
        Args:
            candidate: 候选人信息
            interviewers: 面试官列表
            duration: 面试时长
            is_online: 是否为在线面试
            
        Returns:
            面试安排信息
        """
        try:
            # 找到共同可用时间段
            available_slots = self._find_common_slots(interviewers, candidate)
            
            # 选择最佳时间段
            best_slot = self._select_best_slot(available_slots, duration)
            if not best_slot:
                self.logger.warning("未找到合适的面试时间段")
                return None
                
            # 创建面试记录
            interview = Interview(
                candidate=candidate,
                interviewers=interviewers,
                start_time=best_slot['start'],
                end_time=best_slot['end'],
                location=self._generate_meeting_link() if is_online else "会议室A",
                status="scheduled"
            )
            
            # 通知参与者
            self._notify_participants(interview)
            
            # 保存面试记录
            self.interviews.append(interview)
            
            return interview
            
        except Exception as e:
            self.logger.error(f"安排面试失败: {str(e)}")
            raise
            
    def get_interview_status(self, candidate_email: str) -> Optional[Interview]:
        """获取候选人的面试状态"""
        for interview in self.interviews:
            if interview.candidate.email == candidate_email:
                return interview
        return None
        
    def update_interview_status(self, interview: Interview, 
                              status: str, feedback: Optional[str] = None):
        """更新面试状态和反馈"""
        interview.status = status
        if feedback:
            interview.feedback = feedback
        self.logger.info(f"已更新面试状态：{status}")