# Documentation

## Niveaux de composition

Trois couches successives permettent de suivre composition hiérarchique et conservation des éléments:

 - `Bien` (Good) : objet ou produit qui peut contenir d’autres biens (ex. une voiture contient un pneu, un pneu contient du caoutchouc).

 - `Substance` (Transformable) : matériaux constitutifs des biens (ex. acier, plastique).

 - `Propriétés conservées` (Conserved layer) : éléments et caractéristiques fondamentales conservées (C, H, Fe, HHV, etc.).

Les relations “quantifiées” qui lient un `Bien` ↔ `Substances` ↔ `Propriétés conservées` permettent le calcul “net” à la volée.

## Processus et coefficients

Un `processus` est une activité de transformation (ex. compostage, centrale électrique). 

Chaque processus applique séquentiellement, dans un ordre précis, ou par rééquilibrage, ces coefficients pour générer des inventaires cohérents :

 - `Coefficient de transfert` (TR) : décrit la part d’un élément/substance transférée d’une entrée vers une sortie (ex. 10 % du C de la biomasse → compost).


 - `Coefficient technique` (TE) : besoins/émissions par unité fonctionnelle ou par composition (ex. 1 kWh électricité/kg compost).

 Les processus disposent aussi de `Contraintes` : des limites de conservation, bornes max/min, ratios imposés.



