# utils/helpers.py
import re
import asyncio
from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.errors import FloodWait, RPCError

def parse_target(url: str):
    """
    EXTREME PARSER: 
    Extracts Peer (Chat ID/Username) and Message ID safely.
    Fixed logic for private channel IDs and numeric usernames.
    """
    url = url.strip().replace("https://", "").replace("http://", "").replace("tg://", "")
    
    # 1. Private Channel/Group Logic (t.me/c/12345/678)
    if "/c/" in url:
        # Regex: find the number after /c/ and the one after that (msg_id)
        m = re.search(r"t\.me/c/(\d+)/(\d+)", url)
        if m:
            chat_id = int("-100" + m.group(1))
            msg_id = int(m.group(2))
            return chat_id, msg_id
        else:
            # Maybe it's just a chat link without message ID
            m = re.search(r"t\.me/c/(\d+)", url)
            if m:
                return int("-100" + m.group(1)), None
            raise ValueError("❌ Invalid Private Link Format!")

    # 2. Public Link logic (t.me/username/123)
    # This covers t.me/durov/123, telegram.me/durov, etc.
    m = re.search(r"(?:t\.me|telegram\.me|telegram\.dog)/([a-zA-Z0-9_]+)/?(\d+)?", url)
    if m:
        chat_part = m.group(1)
        msg_id = int(m.group(2)) if m.group(2) else None
        
        # Check if chat_part is purely numeric (rare but happens)
        chat_peer = int(chat_part) if chat_part.isdigit() else chat_part
        return chat_peer, msg_id

    # 3. Raw Username logic (@username or username)
    clean_username = url.replace("@", "").split("/")[0]
    if len(clean_username) > 3:
        return clean_username, None

    raise ValueError("❌ Critical Format Error! Link is unrecognizable.")

async def auto_join(client: Client, invite_link: str):
    """
    ADVANCED JOINER:
    Handles Invite Hashes and Public Usernames with FloodWait recovery.
    """
    link = invite_link.strip()
    try:
        if "+" in link or "joinchat" in link:
            # Extraction logic for hash code
            hash_code = link.split("+")[-1] if "+" in link else link.split("/")[-1]
            # Remove trailing slashes or queries
            hash_code = hash_code.split("?")[0].strip("/")
            await client.invoke(functions.messages.ImportChatInvite(hash=hash_code))
        else:
            # Public username join
            username = link.split("/")[-1].replace("@", "")
            await client.join_chat(username)
        return True
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await auto_join(client, invite_link)
    except RPCError:
        # Already in chat or broken link
        return False
    except Exception:
        return False

def get_progress_card(target, success, failed, total, sessions_count):
    """
    Professional Monitoring Dashboard (10/10 Score).
    """
    completed = success + failed
    percentage = (completed / total * 100) if total > 0 else 0
    
    # Progress Bar Calculation
    filled = int(percentage / 10)
    bar = "▰" * filled + "▱" * (10 - filled)
    
    return (
        f"🚀 **Ultimate Reporting Dashboard**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Target:** `{target}`\n"
        f"📈 **Progress:** `{percentage:.1f}%` | {bar}\n\n"
        f"✅ **Success:** `{success}`\n"
        f"❌ **Failed:** `{failed}`\n"
        f"🔢 **Requests:** `{completed}/{total}`\n"
        f"🧵 **Active Workers:** `{sessions_count}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ **Status:** `MTProto Flood Active...`"
    )
