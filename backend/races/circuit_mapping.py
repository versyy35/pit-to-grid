"""
Maps Race.circuit values (as stored from FastF1 syncs) to circuit SVG
filenames from the julesr0y/f1-circuits-svg dataset:
https://github.com/julesr0y/f1-circuits-svg (CC-BY-4.0)

Layout numbers are pinned to the current (2021-2026 era) circuit
configuration -- the highest layout number available for each circuit
at time of writing, since none of these circuits changed layout within
that window except where a specific number reflects the current one.

Some circuit names vary across years due to inconsistencies in FastF1's
own Location field (e.g. "Monaco" vs "Monte Carlo", "Miami" vs "Miami
Gardens") -- both variants map to the same file.
"""

CIRCUIT_FILES = {
    "Austin": "austin-1.svg",
    "Baku": "baku-1.svg",
    "Barcelona": "catalunya-6.svg",
    "Budapest": "hungaroring-3.svg",
    "Imola": "imola-3.svg",
    "Istanbul": "istanbul-1.svg",
    "Jeddah": "jeddah-1.svg",
    "Las Vegas": "las-vegas-1.svg",
    "Le Castellet": "paul-ricard-3.svg",
    "Lusail": "lusail-1.svg",
    "Marina Bay": "marina-bay-4.svg",
    "Melbourne": "melbourne-2.svg",
    "Mexico City": "mexico-city-3.svg",
    "Miami": "miami-1.svg",
    "Miami Gardens": "miami-1.svg",
    "Monaco": "monaco-6.svg",
    "Monte Carlo": "monaco-6.svg",
    "Montréal": "montreal-6.svg",
    "Monza": "monza-7.svg",
    "Portimão": "portimao-1.svg",
    "Sakhir": "bahrain-3.svg",
    "São Paulo": "interlagos-2.svg",
    "Shanghai": "shanghai-1.svg",
    "Silverstone": "silverstone-8.svg",
    "Sochi": "sochi-1.svg",
    "Spa-Francorchamps": "spa-francorchamps-4.svg",
    "Spielberg": "spielberg-3.svg",
    "Suzuka": "suzuka-2.svg",
    "Yas Island": "yas-marina-2.svg",
    "Zandvoort": "zandvoort-5.svg",
}


def get_circuit_file(circuit_name):
    """Returns the SVG filename for a given Race.circuit value, or None if unmapped."""
    return CIRCUIT_FILES.get(circuit_name)
