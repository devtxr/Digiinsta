import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from .store import products, add_product, toggle_product

bot = Bot(os.environ.get("TELEGRAM_BOT_TOKEN", ""))
dp = Dispatcher(storage=MemoryStorage())

def is_admin(uid):
    return str(uid) in [x.strip() for x in os.environ.get("TELEGRAM_ADMIN_IDS", "").split(",") if x.strip()]

def menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Products", callback_data="products"), InlineKeyboardButton(text="➕ Add Product", callback_data="add")],
        [InlineKeyboardButton(text="🛒 Orders", callback_data="orders"), InlineKeyboardButton(text="📊 Stats", callback_data="stats")],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
    ])

async def start(message: types.Message):
    if not is_admin(message.from_user.id): return await message.answer("⛔ Admin only")
    await message.answer("🛍️ <b>Digital Store Admin</b>\nChoose an action:", reply_markup=menu(), parse_mode="HTML")

dp.message.register(start, lambda m: m.text == "/start")

dp.message.register(start, lambda m: m.text == "/admin")

@dp.message(lambda m: bool(m.text and m.text.startswith("/add ")))
async def add_cmd(message: types.Message):
    if not is_admin(message.from_user.id): return await message.answer("⛔ Admin only")
    parts=[x.strip() for x in message.text[5:].split("|")]
    if len(parts) < 4:
        return await message.answer("Format:\n/add Name | Description | Price | File URL | Image URL(optional)")
    name, desc, price, file_url = parts[:4]
    image_url = parts[4] if len(parts) > 4 else ""
    try: pid=add_product(name, desc, float(price), file_url, image_url)
    except Exception as e: return await message.answer(f"❌ Error: {e}")
    await message.answer(f"✅ Product added\nID: <code>{pid}</code>", parse_mode="HTML", reply_markup=menu())

@dp.callback_query()
async def callbacks(call: types.CallbackQuery):
    if not is_admin(call.from_user.id): return await call.answer("Admin only", show_alert=True)
    data = call.data
    if data == "products":
        ps = products()
        if not ps: return await call.message.edit_text("📦 No products yet.", reply_markup=menu())
        rows=[]
        for p in ps[:30]:
            state = "🟢" if p.get("active") else "🔴"
            rows.append([InlineKeyboardButton(text=f"{state} {p['name']} ₹{p['price']}", callback_data=f"p:{p['_id']}")])
        rows.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back")])
        await call.message.edit_text("📦 <b>Products</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")
    elif data.startswith("p:"):
        from .store import product
        p=product(data[2:])
        if not p: return await call.answer("Not found", show_alert=True)
        kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄 Toggle Active", callback_data=f"toggle:{p['_id']}")],[InlineKeyboardButton(text="⬅️ Back", callback_data="products")]])
        await call.message.edit_text(f"<b>{p['name']}</b>\n₹{p['price']}\n\n{p['description']}\n\nStatus: {'🟢 Active' if p.get('active') else '🔴 Disabled'}", reply_markup=kb, parse_mode="HTML")
    elif data.startswith("toggle:"):
        toggle_product(data[7:]); await call.answer("Updated"); await call.message.edit_text("Updated.", reply_markup=menu())
    elif data == "back":
        await call.message.edit_text("🛍️ <b>Digital Store Admin</b>", reply_markup=menu(), parse_mode="HTML")
    elif data == "add":
        await call.message.answer("➕ Add product via command:\n\n<code>/add name | description | price | file_url | image_url</code>", parse_mode="HTML")
    elif data == "orders":
        from .db import get_db
        count=get_db().orders.count_documents({})
        paid=get_db().orders.count_documents({"payment_status":"paid"})
        await call.message.edit_text(f"🛒 Orders: <b>{count}</b>\n✅ Paid: <b>{paid}</b>", reply_markup=menu(), parse_mode="HTML")
    elif data == "stats":
        from .db import get_db
        db=get_db(); count=db.orders.count_documents({}); paid=db.orders.count_documents({"payment_status":"paid"})
        total=sum((x.get('amount',0) for x in db.orders.find({'payment_status':'paid'})), 0)
        await call.message.edit_text(f"📊 <b>Stats</b>\nOrders: {count}\nPaid: {paid}\nRevenue: ₹{total:.2f}", reply_markup=menu(), parse_mode="HTML")
    else:
        await call.message.edit_text("⚙️ Settings", reply_markup=menu())
    await call.answer()

async def process_update(data):
    update = types.Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
