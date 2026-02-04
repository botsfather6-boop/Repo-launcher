# report.py
import asyncio
import logging
from pyrogram import Client
from pyrogram.raw import functions, types
from pyrogram.errors import RPCError, FloodWait, PeerIdInvalid, ChannelInvalid

logger = logging.getLogger("OxyReport")

async def send_single_report(client: Client, chat_id: int | str, msg_id: int | None, reason_code: str, description: str):
    """
    ULTIMATE REPORT ENGINE v3.5: 
    Handles Peer Sync, FloodWait, and Message vs Profile reporting.
    """
    try:
        # 1. ROBUST PEER SYNC 
        ping_id = chat_id
        try:
            # Direct resolve attempt
            peer = await client.resolve_peer(ping_id)
        except (PeerIdInvalid, ChannelInvalid, KeyError, ValueError):
            try:
                # Force server fetch to sync Peer ID into session state
                chat = await client.get_chat(chat_id)
                peer = await client.resolve_peer(chat.id)
            except Exception as e:
                logger.error(f"Worker {client.name} - Resolution Failed: {e}")
                return False

        # 2. REASON MAPPING (MTProto Schema)
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
        selected_reason = reasons.get(str(reason_code), types.InputReportReasonOther())

        # 3. EXECUTION LOGIC
        if msg_id:
            # Report specific Message
            await client.invoke(
                functions.messages.Report(
                    peer=peer,
                    id=[int(msg_id)],
                    reason=selected_reason,
                    message=description
                )
            )
        else:
            # Report Entire Profile/Channel
            await client.invoke(
                functions.account.ReportPeer(
                    peer=peer,
                    reason=selected_reason,
                    message=description
                )
            )
        
        logger.info(f"Worker {client.name} - Action Success ✅")
        return True

    except FloodWait as e:
        # Skip worker if wait time is too long (>120s) to maintain wave speed
        if e.value > 120:
            logger.warning(f"Worker {client.name} - Skipping (FloodWait: {e.value}s)")
            return False
            
        logger.warning(f"Worker {client.name} - Sleeping {e.value}s")
        await asyncio.sleep(e.value)
        return await send_single_report(client, chat_id, msg_id, reason_code, description)

    except RPCError as e:
        logger.debug(f"Worker {client.name} - API Error: {e.message}")
        return False

    except Exception as e:
        logger.error(f"Worker {client.name} - Internal Error: {e}")
        return False
