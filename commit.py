import pexpect

def confirm_commit(device, admin_current, new_pwds):
    ip = device.get("ip")
    nom = device.get("nom")

    # Utilise le nouveau mdp admin si modifié, sinon l'ancien
    if new_pwds.get("admin"):
        admin_pass = new_pwds["admin"]
    else:
        admin_pass = admin_current

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
            child.sendline(admin_pass)
        elif i == 1:
            child.sendline(admin_pass)
        else:
            return f"[{nom}] Erreur SSH : Connexion échouée."

        child.expect(">")
        child.sendline("configure")
        child.expect("#")
        child.sendline("commit")
        child.expect("#")
        child.sendline("exit")
        child.expect(">")
        child.sendline("exit")
        child.close()

        return f"[{nom}] Commit final validé."
    except Exception as e:
        return f"[{nom}] Erreur commit final: {e}"
