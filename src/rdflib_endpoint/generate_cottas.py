# generate_cottas.py
import pycottas

# Convierte RDF → COTTAS
pycottas.rdf2cottas("personas.ttl", "personas.cottas", index="spo")

print("✅ Archivo personas.cottas generado correctamente.")
