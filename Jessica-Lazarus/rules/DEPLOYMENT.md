# DEPLOYMENT RULES

## Before Deploying ANYTHING
1. **ASK BRUCE FIRST** — "Deploy?" and wait for approval
2. **Backup first** — `cp -r project/ project-backup/`
3. **Test locally** — make sure it builds and works
4. **Check which site** — multiple versions exist, wrong version = wrong content

## Firebase Deployment
```bash
# Bruce Racing
cd projects/bruce-racing-new && firebase deploy --only hosting:bruce-racing-pvt

# Other sites
cd projects/[name] && firebase deploy --only hosting:[name]
```

## Vercel Deployment
```bash
cd projects/[name] && npx vercel --prod --yes
```

## After Deployment
1. **Verify** — check the live URL
2. **Report** — tell Bruce what was deployed
3. **Update NOW.md** — mark as done

## NEVER Deploy These Without Extra Confirmation
- Bruce Racing main site (bruce-racing-pvt.web.app)
- Ask Bruce (ask-bruce.web.app)
- GoGetter Engine (gogetter-engine.vercel.app)
- Any site with customer data

---
*When in doubt, DON'T deploy*
