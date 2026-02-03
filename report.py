# report.py
import asyncio
import logging
from pyrogram import Client
from pyrogram.raw import functions, types
from pyrogram.errors import RPCError, FloodWait

logger = logging.getLogger(__name__)

async def send_single_report(client: Client, chat_id: int | str, msg_id: int | None, reason_code: str, description: str):
    """
    Executes raw API calls to report messages or profiles with automatic FloodWait handling.
    """
    try:
        # Resolve the chat link/ID to a raw Peer object
        peer = await client.resolve_peer(chat_id)
        
        # Mapping frontend codes to Telegram Internal Reason Types
        reasons = {
            '1': types.InputReportReasonSpam(),
            '2': types.InputReportReasonViolence(),
            '3': types.InputReportReasonChildAbuse(),
            '4': types.InputReportReasonPornography(),
            '5': types.InputReportReasonFake(),
            '6': types.InputReportReasonIllegalDrugs(),
            '7': types.InputReportReasonPersonalDetails(),
            '8': types.InputReportReasonOther()
        }
        
        # Fallback to 'Other' if reason_code is invalid
        reason = reasons.get(str(reason_code), types.InputReportReasonOther())

        if msg_id:
            # Logic for reporting a specific message (e.g., t.me/chat/123)
            await client.invoke(
                functions.messages.Report(
                    peer=peer,
                    id=[int(msg_id)], # Must be a list of IDs
                    reason=reason,
                    message=description
                )
            )
        else:
            # Logic for reporting a profile, bot, or channel as a whole
            await client.invoke(
                functions.account.ReportPeer(
                    peer=peer,
                    reason=reason,
                    message=description
                )
            )
        return True

    except FloodWait as e:
        # CRITICAL FIX: Automatically wait and retry if Telegram throttles the session
        logger.warning(f"Session {client.name} hitting FloodWait: Sleeping {e.value}s")
        await asyncio.sleep(e.value)
        return await send_single_report(client, chat_id, msg_id, reason_code, description)

    except RPCError as e:
        # Handle specific Telegram API errors (e.g., PeerIdInvalid)
        logger.error(f"Telegram API Error on session {client.name}: {e.message}")
        return False

    except Exception as e:
        # Catch unexpected errors to prevent bot crash
        logger.error(f"Unexpected error in report execution: {e}")
        return False
