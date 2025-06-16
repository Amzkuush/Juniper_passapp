from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import yaml
import os
from deploy import deploy_passwords
from commit import confirm_commit

app = FastAPI()
templates = Jinja2Templates(directory="templates")

INVENTORY_FILE = "inventory.yaml"

def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "r") as f:
            data = yaml.safe_load(f)
            if data and "equipements" in data:
                return data["equipements"]
    return []

def save_inventory(equipements):
    with open(INVENTORY_FILE, "w") as f:
        yaml.dump({"equipements": equipements}, f)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    equipements = load_inventory()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "equipements": equipements,
        "result": ""
    })

@app.post("/deploy", response_class=HTMLResponse)
async def deploy(request: Request,
           admin_pass_ex: str = Form(None),
           root_pass_ex: str = Form(None),
           admin_pass_new_ex: str = Form(None),
           oxidized_pass_ex: str = Form(None),
           admin_pass_mx: str = Form(None),
           root_pass_mx: str = Form(None),
           admin_pass_new_mx: str = Form(None),
           oxidized_pass_mx: str = Form(None),
           ipsisupadm_pass: str = Form(None)):

    equipements = load_inventory()
    results = []

    if admin_pass_ex:
        new_pwds_ex = {
            "root": root_pass_ex,
            "admin": admin_pass_new_ex,
            "oxidized": oxidized_pass_ex,
            "admin_current": admin_pass_ex
        }
        for device in equipements:
            if device.get("type", "").upper() == "EX":
                results.append(deploy_passwords(device, new_pwds_ex))

    if admin_pass_mx:
        new_pwds_mx = {
            "root": root_pass_mx,
            "admin": admin_pass_new_mx,
            "oxidized": oxidized_pass_mx,
            "IpsiSupAdm": ipsisupadm_pass,
            "admin_current": admin_pass_mx
        }
        for device in equipements:
            if device.get("type", "").upper() == "MX":
                results.append(deploy_passwords(device, new_pwds_mx))

    if not results:
        results.append("Aucun déploiement effectué : mot de passe admin actuel manquant.")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "equipements": equipements,
        "result": "\n\n".join(results)
    })

@app.post("/commit", response_class=HTMLResponse)
async def commit_final(request: Request,
                       admin_pass_ex: str = Form(None),
                       root_pass_ex: str = Form(None),
                       admin_pass_new_ex: str = Form(None),
                       oxidized_pass_ex: str = Form(None),
                       admin_pass_mx: str = Form(None),
                       root_pass_mx: str = Form(None),
                       admin_pass_new_mx: str = Form(None),
                       oxidized_pass_mx: str = Form(None),
                       ipsisupadm_pass: str = Form(None)):

    equipements = load_inventory()
    results = []

    new_pwds_ex = {
        "root": root_pass_ex,
        "admin": admin_pass_new_ex,
        "oxidized": oxidized_pass_ex
    }
    new_pwds_mx = {
        "root": root_pass_mx,
        "admin": admin_pass_new_mx,
        "oxidized": oxidized_pass_mx,
        "IpsiSupAdm": ipsisupadm_pass
    }

    for device in equipements:
        dev_type = device.get("type", "").upper()
        if dev_type == "EX" and admin_pass_ex:
            results.append(confirm_commit(device, admin_pass_ex, new_pwds_ex))
        elif dev_type == "MX" and admin_pass_mx:
            results.append(confirm_commit(device, admin_pass_mx, new_pwds_mx))
        else:
            results.append(f"[{device.get('nom')}] Mot de passe admin actuel manquant pour commit.")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "equipements": equipements,
        "result": "\n\n".join(results)
    })

@app.post("/add_device", response_class=HTMLResponse)
async def add_device(request: Request,
               nom: str = Form(...),
               ip: str = Form(...),
               type: str = Form(...)):

    equipements = load_inventory()
    type_upper = type.strip().upper()
    if type_upper not in ["EX", "MX"]:
        result = f"Type '{type}' non valide. Utilisez 'EX' ou 'MX'."
        return templates.TemplateResponse("index.html", {
            "request": request,
            "equipements": equipements,
            "result": result
        })

    for eq in equipements:
        if eq["ip"] == ip:
            result = f"Un équipement avec l'IP {ip} existe déjà."
            return templates.TemplateResponse("index.html", {
                "request": request,
                "equipements": equipements,
                "result": result
            })

    equipements.append({"nom": nom, "ip": ip, "type": type_upper})
    save_inventory(equipements)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_device", response_class=HTMLResponse)
async def delete_device(request: Request, ip: str = Form(...)):
    equipements = load_inventory()
    equipements = [eq for eq in equipements if eq["ip"] != ip]
    save_inventory(equipements)
    return RedirectResponse(url="/", status_code=303)
