#!/usr/bin/env python3
# main.py - Основной бот для массовых жалоб
import asyncio
import logging
import random
import os
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import (
    InputReportReasonSpam, 
    InputReportReasonViolence, 
    InputReportReasonPornography, 
    InputReportReasonOther
)

from config import (
    API_ID, API_HASH, BOT_TOKEN, ACCOUNTS,
    REPORT_TEXTS, MIN_DELAY, MAX_DELAY,
    DEFAULT_REPORT_COUNT, LOG_LEVEL
)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REPORT_REASONS_MAP = {
    "spam": InputReportReasonSpam(),
    "violence": InputReportReasonViolence(),
    "pornography": InputReportReasonPornography(),
    "other": InputReportReasonOther()
}

class MassReportBot:
    def __init__(self):
        self.bot = None
        self.clients = []
        
    async def init_bot(self):
        """Инициализация основного бота"""
        self.bot = TelegramClient("bot_session", API_ID, API_HASH)
        await self.bot.start(bot_token=BOT_TOKEN)
        logger.info("Основной бот запущен")
        
    async def init_clients(self):
        """Инициализация клиентов для отправки жалоб"""
        self.clients = []
        
        # Создаём папку для сессий
        os.makedirs("sessions", exist_ok=True)
        
        for account in ACCOUNTS:
            session_name = account["session"]
            try:
                client = TelegramClient(session_name, API_ID, API_HASH)
                await client.connect()
                
                if not await client.is_user_authorized():
                    logger.warning(f"Аккаунт {account['phone']} не авторизован")
                    continue
                    
                self.clients.append(client)
                me = await client.get_me()
                logger.info(f"Загружен: {me.first_name} (@{me.username})")
                
            except Exception as e:
                logger.error(f"Ошибка загрузки {account['phone']}: {e}")
        
        logger.info(f"Загружено {len(self.clients)} аккаунтов")
        
    async def send_report(self, client, target_username, reason_type="spam", custom_text=None):
        """Отправка одной жалобы"""
        try:
            entity = await client.get_entity(target_username)
            messages = await client.get_messages(entity, limit=3)
            message_ids = [msg.id for msg in messages if msg] or [0]
            
            reason = REPORT_REASONS_MAP.get(reason_type, REPORT_REASONS_MAP["other"])
            text = custom_text or random.choice(REPORT_TEXTS)
            unique_suffix = f" [ref:{random.randint(1000, 9999)}]"
            
            result = await client(ReportRequest(
                peer=entity,
                id=message_ids,
                reason=reason,
                message=text + unique_suffix
            ))
            
            return True, text
            
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return False, str(e)
    
    async def mass_report(self, target_username, count=None):
        """Массовая отправка жалоб"""
        if not self.clients:
            await self.init_clients()
        
        if not self.clients:
            return {"status": "error", "message": "Нет доступных аккаунтов"}
        
        count = count if count and count <= len(self.clients) else len(self.clients)
        successful = 0
        failed = 0
        details = []
        
        shuffled = self.clients.copy()
        random.shuffle(shuffled)
        
        for i, client in enumerate(shuffled[:count]):
            reason = random.choice(list(REPORT_REASONS_MAP.keys()))
            text = random.choice(REPORT_TEXTS)
            
            logger.info(f"[{i+1}/{count}] Отправка жалобы...")
            
            success, result = await self.send_report(client, target_username, reason, text)
            
            if success:
                successful += 1
                details.append(f"✅ Аккаунт #{i+1}: жалоба отправлена")
            else:
                failed += 1
                details.append(f"❌ Аккаунт #{i+1}: ошибка")
            
            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        
        return {
            "status": "completed",
            "target": target_username,
            "total": count,
            "successful": successful,
            "failed": failed,
            "details": details[:10],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def run(self):
        """Запуск бота"""
        await self.init_bot()
        await self.init_clients()
        
        @self.bot.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await event.reply(f"""🤖 *Mass Report Bot*
            
⚡ *Статус:* {len(self.clients)} аккаунтов
⏱️ *Задержка:* {MIN_DELAY}-{MAX_DELAY} сек

/report @username - отправить жалобы
/report @username 10 - отправить 10
/status - статус системы""", parse_mode='markdown')
        
        @self.bot.on(events.NewMessage(pattern='/report (\\S+)(?:\\s+(\\d+))?'))
        async def report_handler(event):
            target = event.pattern_match.group(1)
            count = int(event.pattern_match.group(2)) if event.pattern_match.group(2) else None
            
            if not target.startswith('@'):
                target = '@' + target
            
            await event.reply(f"🎯 Отправка жалоб на {target}...")
            
            result = await self.mass_report(target, count)
            
            if result["status"] == "completed":
                msg = f"""✅ *Отчёт*

🎯 Цель: {result["target"]}
📨 Успешно: {result["successful"]}/{result["total"]}
❌ Ошибок: {result["failed"]}"""
                await event.reply(msg, parse_mode='markdown')
        
        @self.bot.on(events.NewMessage(pattern='/status'))
        async def status_handler(event):
            active = len([c for c in self.clients if c.is_connected()])
            await event.reply(f"""📊 *Статус*

Аккаунтов: {len(self.clients)} (активно: {active})
Задержка: {MIN_DELAY}-{MAX_DELAY} сек""", parse_mode='markdown')
        
        logger.info("Бот запущен")
        await self.bot.run_until_disconnected()

if __name__ == "__main__":
    bot = MassReportBot()
    asyncio.run(bot.run())
