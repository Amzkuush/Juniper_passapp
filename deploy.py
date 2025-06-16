import pexpect

def deploy_passwords(device, new_pwds):
    ip = device.get("ip")
    nom = device.get("nom")
    admin_current = new_pwds.get("admin_current")
    if not admin_current:
        return f"[{nom}] Mot de passe admin actuel manquant pour déploiement."

    try:
        child = pexpect.spawn(f"ssh admin@{ip}", timeout=30)
        i = child.expect([
            "Are you sure you want to continue connecting (yes/no/[fingerprint])?",
            "password:",
            pexpect.EOF,
            pexpect.TIMEOUT
        ])
        if i == 0:
            child.sendline("yes")
            child.expect("password:")
            child.sendline(admin_current)
        elif i == 1:
            child.sendline(admin_current)
        else:
            return f"[{nom}] Erreur SSH : Connexion échouée."

        child.expect(">")
        child.sendline("configure")
        child.expect("#")

        # Exemple : changer le mot de passe root si fourni
        if new_pwds.get("root"):
            child.sendline(f"set system root-authentication plain-text-password")
            child.expect("New password:")
            child.sendline(new_pwds["root"])
            child.expect("Retype new password:")
            child.sendline(new_pwds["root"])
            child.expect("#")

        # changer mot de passe admin si fourni
        if new_pwds.get("admin"):
            child.sendline(f"set system login user admin authentication plain-text-password")
            child.expect("New password:")
            child.sendline(new_pwds["admin"])
            child.expect("Retype new password:")
            child.sendline(new_pwds["admin"])
            child.expect("#")

        # changer mot de passe oxidized si fourni
        if new_pwds.get("oxidized"):
            child.sendline(f"set system login user oxidized authentication plain-text-password")
            child.expect("New password:")
            child.sendline(new_pwds["oxidized"])
            child.expect("Retype new password:")
            child.sendline(new_pwds["oxidized"])
            child.expect("#")

        # Pour MX, changer aussi IpsiSupAdm si présent
        if new_pwds.get("IpsiSupAdm"):
            child.sendline(f"set system login user IpsiSupAdm authentication plain-text-password")
            child.expect("New password:")
            child.sendline(new_pwds["IpsiSupAdm"])
            child.expect("Retype new password:")
            child.sendline(new_pwds["IpsiSupAdm"])
            child.expect("#")

        # Commit confirmed 20
        child.sendline("commit confirmed 20")
        child.expect("#")
        child.sendline("exit")
        child.expect(">")
        child.sendline("exit")
        child.close()

        return f"[{nom}] Déploiement des mots de passe réussi."
    except Exception as e:
        return f"[{nom}] Erreur déploiement : {e}"
