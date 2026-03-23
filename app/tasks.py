# app/tasks.py
from app.celery_worker import celery
from loguru import logger

@celery.task(bind=True, max_retries=3)
def send_policy_created_notification(self, policy_id: int, request_id: str):
    """保单创建成功后发送通知（邮件、审计、外部系统同步等）"""
    try:
        logger.info(f"Notification task started for policy {policy_id} | request_id={request_id}")
        # 这里可以加真实邮件发送、Webhook 调用等逻辑
        logger.success(f"Notification sent successfully for policy {policy_id}")
    except Exception as exc:
        logger.error(f"Notification failed, retrying... | request_id={request_id}")
        raise self.retry(exc=exc, countdown=60)