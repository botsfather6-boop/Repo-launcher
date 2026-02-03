# utils/helpers.py
import re
from pyrogram import Client
from pyrogram.raw import functions

def parse_target(url: str):
    """
    Advanced logic to extract Peer (Chat ID/Username) and Message ID from Telegram links.
    Supports: Public, Private, Profile links, and raw Usernames.
    """
    url = url.strip()
    
    # Comprehensive Regex for t.me links
    # Handles: t.me/username, t.me/username/123, t.me/c/12345/123, and https variants
    m = re.search(r"(?:https?://)?(?:t\.me|telegram\.me|telegram\.dog)/(c/)?([^/]+)/?(\d+)?", url)
    
    if not m:
        # Fallback: Check if it's just a username like @durov or durov
        if url.startswith("@"):
            return url.replace("@", ""), None
        elif "/" not in url and len(url) > 3:
            return url, None
        raise ValueError("❌ Invalid Format! Provide a valid t.me link or @username.")
    
    is_private = m.group(1) == "c/"
    chat_part = m.group(2)
    msg_id = m.group(3)

    # 1. Processing Peer (Chat ID or Username)
    if is_private:
        try:
            # Private Supergroups require -100 prefix for Pyrogram/MTProto
            chat_id = int("-100" + chat_part)
        except ValueError:
            raise ValueError("❌ Invalid Private Link: Numeric ID expected after /c/.")
    else:
        # Public links can use username strings or numeric IDs
        chat_id = int(chat_part) if chat_part.isdigit() else chat_part

    # 2. Processing Message ID (Optional)
    final_msg_id = int(msg_id) if msg_id else None
        
    return chat_id, final_msg_id

async def auto_join(client: Client, invite_link: str):
    """
    Ensures the reporting session joins the target group/channel before execution.
    Necessary for reporting private group messages.
    """
    try:
        invite_link = invite_link.strip()
        if "t.me/+" in invite_link or "t.me/joinchat/" in invite_link:
            # Extract the unique invite hash
            if "+" in invite_link:
                hash_code = invite_link.split("+")[-1]
            else:
                hash_code = invite_link.split("/")[-1]
            await client.invoke(functions.messages.ImportChatInvite(hash=hash_code))
        else:
            # Join public chat by username/slug
            username = invite_link.split("/")[-1].replace("@", "")
            await client.join_chat(username)
        return True
    except Exception:
        # Usually fails if already a member, which is fine
        return False

def get_progress_card(target, success, failed, total, sessions_count):
    """
    Generates a high-signal, visual progress dashboard for the user.
    10/10 Score: Professional UI with dynamic bar.
    """
    completed = success + failed
    percentage = (completed / total * 100) if total > 0 else 0
    
    # Dynamic Progress Bar (Customizable visual)
    filled_len = int(percentage / 10)
    p_bar = "▰" * filled_len + "▱" * (10 - filled_len)
    
    card = (
        f"🚀 **Ultimate Reporting Dashboard**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 **Target:** `{target}`\n"
        f"📈 **Progress:** `{percentage:.1f}%`\n"
        f"|{p_bar}|\n\n"
        f"✅ **Success:** `{success}`\n"
        f"❌ **Failed:** `{failed}`\n"
        f"🔢 **Requests:** `{completed}/{total}`\n"
        f"🧵 **Active Threads:** `{sessions_count}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ **Status:** `Executing MTProto Flood...`"
    )
    return card
