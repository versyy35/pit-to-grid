"""
Maps Race.circuit values (as stored from FastF1 syncs) to circuit slugs
used by the julesr0y/f1-circuits-svg dataset:
https://github.com/julesr0y/f1-circuits-svg (CC-BY-4.0)

Some circuit names vary across years due to inconsistencies in FastF1's
own Location field (e.g. "Monaco" vs "Monte Carlo", "Miami" vs "Miami
Gardens") -- both variants are mapped to the same slug here.
"""

CIRCUIT_SLUGS = {
    "Austin": "austin",
    "Baku": "baku",
    "Barcelona": "catalunya",
    "Budapest": "hungaroring",
    "Imola": "imola",
    "Istanbul": "istanbul",
    "Jeddah": "jeddah",
    "Las Vegas": "las-vegas",
    "Le Castellet": "paul-ricard",
    "Lusail": "lusail",
    "Marina Bay": "marina-bay",
    "Melbourne": "melbourne",
    "Mexico City": "mexico-city",
    "Miami": "miami",
    "Miami Gardens": "miami",
    "Monaco": "monaco",
    "Monte Carlo": "monaco",
    "Montréal": "montreal",
    "Monza": "monza",
    "Portimão": "portimao",
    "Sakhir": "bahrain",
    "São Paulo": "interlagos",
    "Shanghai": "shanghai",
    "Silverstone": "silverstone",
    "Sochi": "sochi",
    "Spa-Francorchamps": "spa-francorchamps",
    "Spielberg": "spielberg",
    "Suzuka": "suzuka",
    "Yas Island": "yas-marina",
    "Zandvoort": "zandvoort",
}


def get_circuit_slug(circuit_name):
    """Returns the SVG slug for a given Race.circuit value, or None if unmapped."""
    return CIRCUIT_SLUGS.get(circuit_name)
