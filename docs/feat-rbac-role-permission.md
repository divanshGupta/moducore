# Why I build a minimal RBAC layer now, not full CRUD

- Two options: 

1. Full Role/Permission CRUD + admin UI first, then RBAC enforcement, then Inventory 

<Pros> "Complete" RBAC before touching business features

<Cons> Slower — we would be building admin tooling for a system with no business routes to protect yet. Risk of gold-plating something we can't demo

2. Minimal RBAC (seed script + require_permission() dependency), then build Inventory routes with permission checks from day one 

<Pros> Every Inventory route gets protected as we write it — no retrofit later. Matches our moducore.md design (medicine.read, medicine.create etc. are literally our example permissions)

<Cons> Role/Permission admin CRUD (inviting users, assigning roles via UI) is deferred — but that's genuinely a later concern, not a blocker

## What "minimal" actually means — scoped small, deliberately

1. Fix the role_permissions/user_roles FK drift first — small, isolated migration, finally giving it the "own day" we deferred twice <DONE>

2. A seed script (not admin CRUD) — creates the roles/permissions from moducore.md (Admin, Pharmacist, Cashier, Manager; medicine.read/create/update/delete) and wires up sensible defaults. CRUD for managing these via API is a legitimate future task, not needed to unblock Inventory work. <DONE>

3. require_permission(permission: str) — a FastAPI dependency, same shape as get_current_user, that loads the user's roles → permissions and checks membership

<CONCEPT> what does this dependency need to do, step by step?

- Get the current authenticated user (reuse get_current_user — don't duplicate token-decoding logic)
- Load that user's roles → permissions (you already have User.roles and Role.permissions relationships wired via selectinload patterns)
- Check whether the requested permission string is in that set
- If yes, let the request through; if no, 403 Forbidden (not 401 — the user is authenticated, they're just not authorized for this specific action — an important distinction to keep straight in your API)

<Design_Decision> how does a route say "I need medicine.create"?

- FastAPI dependencies are normally parameterless in the Depends(...) call, but you need to pass in which permission a given route requires. The clean way to do this is a dependency factory — a function that returns a dependency, closing over the permission string

4. One test route to prove it — reuse /users/me-style pattern, or a throwaway protected-by-permission route, verified before moving to real Inventory routes

- Once it's done, every Hospital Inventory route becomes Depends(require_permission("medicine.create")) for the rest of the project, basically free.