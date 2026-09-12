## Boekingsregels
- De email van de gebruiker is uniek
- Een boeking hoort altijd bij één gebruiker en één ruimte
- `start_at` moet vóór `end_at` liggen
- Voor dezelfde ruimte mogen twee actieve boekingen niet qua tijd overlappen
- Geannuleerde boekingen worden niet meegerekend bij het controleren van de beschikbaarheid
- Voorzieningen worden aan ruimtes gekoppeld via `space_facilities`
