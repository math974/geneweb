# Format .gw - Spécification

## Vue d'ensemble

Le format `.gw` est le format texte de GeneWeb pour décrire des données généalogiques.

## Structure globale

```
encoding: utf-8
gwplus

[familles et personnes]
```

## Famille (`fam`)

```
fam Nom Prénom.occurrence dates attributs + Nom_conjoint Prénom_conjoint dates attributs
```

### Attributs de personne dans `fam`:
- `#occu` : Occupation/profession
- `#src` : Source
- Dates : année ou jour/mois/année
- `<date` : Avant (before)
- `od` : Flag (origin doubt?)

### Événements de famille (`fevt`):
```
fevt
#marr date #p lieu #s source
#div date #p lieu #s source
#<event> date #p lieu #s source
end fevt
```

### Enfants (`beg`/`end`):
```
beg
- h Prénom dates attributs    # Homme
- f Prénom dates attributs    # Femme
end
```

Attributs enfants:
- `od` : Only daughter/son?
- `#src` : Source
- `#bp` : Birth place
- `#bs` : Birth source
- `#dp` : Death place
- `#ds` : Death source

## Événements de personne (`pevt`)

```
pevt Nom Prénom
#birt date #p lieu #s source
#deat date #p lieu #s source
#bapm date #p lieu #s source
#buri date #p lieu #s source
end pevt
```

Événements possibles:
- `#birt` : Naissance (birth)
- `#deat` : Décès (death)
- `#bapm` : Baptême (baptism)
- `#buri` : Inhumation (burial)
- `#crem` : Crémation

Modificateurs:
- `#p` : Lieu (place)
- `#s` : Source
- `#bp` : Birth place
- `#dp` : Death place
- `#mp` : Marriage place
- `#ms` : Marriage source

## Notes

```
notes Nom Prénom
beg
Texte libre avec wiki markup
<br> pour retour à la ligne
[[[Nom Prénom/Patronyme]]] pour lien
<img src="..."> pour images
end notes
```

## Sources (`src`, `csrc`)

```
src identifiant_source
csrc identifiant_source_conjoint
```

## Dates

Formats:
- Année seule: `1789`
- Mois/Année: `8/1789`
- Jour/Mois/Année: `15/8/1789`
- Avant: `<1789`
- Après: `>1789`
- Circa: `~1789`
- Maybe: `?1789`
- Ou: `1789|1790`
- Intervalle: `1789..1790`

## Lieux

Format avec italiques:
```
_[nom court]_-_Nom complet,code postal,département,région,pays
```

Exemple:
```
_[Châlons-sur-Marne]_-_Châlons-en-Champagne,51,Marne,Champagne-Ardenne,France
```

## Noms

Format:
```
Nom Prénom.occurrence
```

- `Nom` : Patronyme (surname)
- `Prénom` : Prénom (first name), peut contenir `_` pour espaces
- `.occurrence` : Numéro d'occurrence (0 par défaut)

Exemples:
- `Galichet Jean_Pierre` → Jean Pierre Galichet
- `Galichet Jean_Pierre.1` → Jean Pierre.1 Galichet
- `Boizot Jean.1234` → Jean.1234 Boizot

## Ordre de lecture

1. `encoding:`
2. `gwplus`
3. Familles (`fam`) avec leurs enfants
4. Sources (`src`, `csrc`)
5. Événements de famille (`fevt`)
6. Notes (`notes`)
7. Événements de personne (`pevt`)

## Exemple complet

```gw
encoding: utf-8
gwplus

fam Galichet Jean_Pierre #occu Marchand 1800 + Loche Marie 1805
src registre_paroissial
fevt
#marr 1825 #p Paris,75,France
end fevt
beg
- h Jean 1826 1890
- f Marie 1828
end

pevt Galichet Jean
#birt 1826 #p Paris,75,France
#deat 1890 #p Lyon,69,France
end pevt

notes Galichet Jean
beg
Notes sur Jean Galichet
end notes
```
