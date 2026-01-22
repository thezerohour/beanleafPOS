BeanLeaf POS – AI Agent Guide

- Goal: Telegram-based POS; persistence is Google Sheets (no DB server). Entry initializes env + Sheets then wires handlers in [src/main.ts](src/main.ts).
- Build/run: `npm run build` → `npm start`; dev hot-run is `npm run dev`; watch TS with `npm run watch`. TypeScript strict is on ([tsconfig.json](tsconfig.json)).
- Env: requires BOT_TOKEN, GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_FILE (defaults to `credentials.json` in project root). dotenv loads in code.

Architecture
- Bot wiring: [src/main.ts](src/main.ts) sets up Telegraf + `session()` middleware; command/callback routing is centralized here.
- Handlers: customer/admin/order flows live in [src/handlers](src/handlers) and are exported via [src/handlers/index.ts](src/handlers/index.ts).
- Models: Google Sheets adapters in [src/models](src/models). `database.ts` caches worksheets and provides add/update/find helpers; models convert booleans to strings for storage.
- Utilities: [src/utils/keyboards.ts](src/utils/keyboards.ts) centralizes inline keyboards; [src/utils/helpers.ts](src/utils/helpers.ts) provides `getOrCreateUser`, formatting helpers, and admin checks.
- Context typing: [src/types.ts](src/types.ts) defines `BotContext` with optional `session.cart` (map of productId → quantity).

Data + Google Sheets
- Sheets and headers are created on startup in `initDb()` within [src/models/database.ts](src/models/database.ts); IDs are assigned by scanning rows (`getNextId`).
- Credential file path is resolved relative to repo root; missing or mis-shared service account will fail startup before bot launch.
- Stored booleans (`is_admin`, `is_available`) are persisted as strings; constructors convert string → boolean on load.

Bot interaction patterns
- Callback data conventions: `product_<id>`, `addcart_<id>`, `order_view_<id>`, `order_complete_<id>`, `order_cancel_<id>`, `admin_edit_<id>`, `admin_toggle_<id>`; keep this style for new actions.
- Always `answerCbQuery()` before heavy work; admin-only actions re-check via `getOrCreateUser` (no reliance on env-only flags).
- Cart state lives in `ctx.session.cart`; stock checks guard add-to-cart and checkout flows.
- Inline keyboards are built with Markup helpers from [src/utils/keyboards.ts](src/utils/keyboards.ts); reuse/extend there instead of ad-hoc layouts.

Notable behaviors
- Checkout in [src/handlers/orders.ts](src/handlers/orders.ts) creates an order row, writes order items, clears the session cart, and leaves stock unchanged until completion.
- Completing an order decrements product stock; cancellation only flips status.
- Errors are logged and surfaced to users via concise replies; bot-level errors are caught with `bot.catch` in [src/main.ts](src/main.ts).

Working tips
- For new Sheet-backed entities, mirror the pattern: define headers in `initDb`, model with constructors handling string→type coercion, CRUD via database helpers.
- When editing messages, expect "message is not modified" errors; see `viewProduct` for defensive handling.
- Keep replies Markdown-safe and pass `parse_mode: 'Markdown'` when formatting text blocks.

Debugging
- Startup failures usually trace to missing env vars or unshared service account access to the target sheet.
- Session issues: ensure middleware remains `bot.use(session())`; cart assumes this is present.
