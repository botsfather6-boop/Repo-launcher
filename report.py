# report.py
import asyncio
import logging
from pyrogram import Client
from pyrogram.raw import functions, types
from pyrogram.errors import (
    RPCError,
    FloodWait,
    PeerIdInvalid,
    ChannelInvalid,
    ChannelPrivate,
    UsernameInvalid,
    UsernameNotOccupied,
    UserNotParticipant
)

logger = logging.getLogger("OxyReport")


async def resolve_peer_safely(client: Client, chat_id: int | str):
    """
    FULL SAFE PEER RESOLVER
    - Normalizes link / username / id
    - Checks joined or not
    - NEVER raises PeerIdInvalid
    """

    try:
        # ---- Normalize ----
        if isinstance(chat_id, str):
            chat_id = chat_id.strip()
            if chat_id.startswith("https://t.me/"):
                chat_id = chat_id.split("/")[-1]
            elif chat_id.startswith("t.me/"):
                chat_id = chat_id.split("/")[-1]

        # ---- Force server sync ----
        chat = await client.get_chat(chat_id)

        # ---- JOIN CHECK (MOST IMPORTANT) ----
        try:
            member = await client.get_chat_member(chat.id, "me")

            # Left / kicked = not allowed
            if member.status in ("left", "kicked"):
                return None

        except (UserNotParticipant, RPCError):
            return None

        # ---- Warm dialogs cache (pyrogram bug fix) ----
        async for _ in client.get_dialogs(limit=1):
            break

        # ---- Final resolve ----
        try:
            return await client.resolve_peer(chat.id)
        except PeerIdInvalid:
            return None

    except (ChannelPrivate, ChannelInvalid):
        return None
    except (UsernameInvalid, UsernameNotOccupied):
        return None
    except RPCError:
        return None
    except Exception:
        return None


async def send_single_report(
    client: Client,
    chat_id: int | str,
    msg_id: int | None,
    reason_code: str,
    description: str
) -> bool:
    """
    CRASH-PROOF REPORT FUNCTION
    """

    peer = await resolve_peer_safely(client, chat_id)
    if not peer:
        logger.debug(f"{client.name}: Skipped (not joined / private)")
        return False

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
    reason = reasons.get(str(reason_code), types.InputReportReasonOther())

    try:
        if msg_id:
            await client.invoke(
                functions.messages.Report(
                    peer=peer,
                    id=[int(msg_id)],
                    reason=reason,
                    message=description
                )
            )
        else:
            await client.invoke(
                functions.account.ReportPeer(
                    peer=peer,
                    reason=reason,
                    message=description
                )
            )
        return True

    except FloodWait as e:
        if e.value > 120:
            logger.warning(f"{client.name}: FloodWait {e.value}s, skipping")
            return False
        await asyncio.sleep(e.value)
        return await send_single_report(
            client, chat_id, msg_id, reason_code, description
        )

    except RPCError:
        return False
    except Exception:
        return False
