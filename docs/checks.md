# Les vérifications en détail

## `indexabilite` — le défaut le plus fréquent

Odoo décide de l'indexabilité par une condition unique, dans
`addons/website/views/website_templates.xml` :

```xml
<template id="robots">
User-agent: *
<t t-if="website.domain and not website._is_indexable_url(url_root)">
Disallow: /
Sitemap: <t t-esc="website.domain"/>/sitemap.xml
</t>
<t t-else="">
Sitemap: <t t-esc="url_root"/>sitemap.xml
</t>
</template>
```

`_is_indexable_url` compare l'hôte demandé au champ « Nom de domaine » des
paramètres du site, en ignorant `www.` et le protocole. Si les deux ne
correspondent pas, l'hôte reçoit `Disallow: /` **et** une balise
`<meta name="robots" content="noindex">`.

Conséquences pratiques :

- une préproduction sur un autre hôte est automatiquement exclue — c'est voulu ;
- le sous-domaine `.odoo.com` d'origine devient invisible dès qu'un domaine
  personnalisé est configuré ;
- une erreur de saisie dans ce champ suffit à désindexer le site de production
  entier, sans aucun message d'erreur.

Le dernier cas est le plus coûteux, et le plus difficile à voir : tout paraît
normal dans l'interface.

## `gestionnaire_bases`

`/web/database/manager` permet de lister, dupliquer, sauvegarder et supprimer
les bases. Exposé publiquement, c'est une prise directe sur les données.

Correction dans `odoo.conf` :

```ini
list_db = False
admin_passwd = <mot de passe long et unique>
```

## `version`

La version est lue dans le chemin des assets (`/web/assets/17.0-…/`). Sous la
16.0, les correctifs de sécurité ne sont plus garantis. Un reverse proxy qui
réécrit ces URL rendra la détection muette — c'est une limite assumée.

## `https`, `en_tetes_securite`, `sitemap`

Vérifications génériques : HTTPS et HSTS, présence de `Content-Security-Policy`,
`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, et disponibilité
de `/sitemap.xml` que le module Site web génère normalement.
