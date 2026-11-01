"""Item inventories and DEMATEL factors used in the MSc thesis (Tables 2.3 and 3.3)."""

CE_CLUSTERS = {
    "A": "Design for disassembly and deconstruction",
    "B": "Design for longevity and adaptability",
    "C": "Reuse and reclamation practices",
    "D": "Refurbishment, repurposing and recycling practices",
    "E": "Material efficiency and waste minimisation",
    "F": "Information and enabling infrastructure",
}

CE_ITEMS = [
    ("CE01", "A", "Use of reversible mechanical connections"),
    ("CE02", "A", "Accessibility of components for later recovery"),
    ("CE03", "A", "Avoidance of bonded and composite assemblies"),
    ("CE04", "A", "Layered construction separating structure, envelope and services"),
    ("CE05", "A", "Deconstruction planning at design stage"),
    ("CE06", "A", "Specification of separable material streams"),
    ("CE07", "B", "Design for extended building service life"),
    ("CE08", "B", "Spatial adaptability and functional flexibility"),
    ("CE09", "B", "Structural capacity provision for future change"),
    ("CE10", "B", "Durability specification of exposed elements"),
    ("CE11", "C", "Direct reuse of reclaimed structural components"),
    ("CE12", "C", "Reuse of reclaimed masonry and blockwork"),
    ("CE13", "C", "Reuse of doors, windows, fittings and fixtures"),
    ("CE14", "C", "Salvage-oriented demolition practice"),
    ("CE15", "D", "Refurbishment of existing building fabric"),
    ("CE16", "D", "Repurposing of components to new functions"),
    ("CE17", "D", "Use of recycled aggregate in concrete"),
    ("CE18", "D", "Recycled content in non-structural elements"),
    ("CE19", "D", "Recovery of demolition waste for secondary use"),
    ("CE20", "E", "Dimensional coordination to reduce off-cuts"),
    ("CE21", "E", "Standardisation and modular component sizing"),
    ("CE22", "E", "Structural optimisation to reduce material quantity"),
    ("CE23", "E", "Prefabrication and off-site manufacture"),
    ("CE24", "E", "Local sourcing to reduce transport burden"),
    ("CE25", "F", "Material passports and component documentation"),
    ("CE26", "F", "BIM-based material inventory"),
    ("CE27", "F", "Reverse logistics and take-back arrangements"),
    ("CE28", "F", "Availability and maturity of secondary material markets"),
    ("CE29", "F", "Professional training in deconstruction principles"),
]

NZS_GROUPS = {
    "S1": "Passive form and ventilation",
    "S2": "Technology- and material-intensive operational measures",
    "S3": "Low-carbon materials and structural efficiency",
    "S4": "Whole-life carbon assessment and targets",
}

NZS_ITEMS = [
    ("NZS01", "S1", "Orientation"), ("NZS02", "S1", "Form and compactness"),
    ("NZS03", "S1", "Courtyards and atria"), ("NZS04", "S1", "Window-to-wall ratio"),
    ("NZS05", "S1", "Cross-ventilation"), ("NZS06", "S1", "Stack-effect ventilation"),
    ("NZS07", "S1", "Night purge ventilation"), ("NZS08", "S2", "Adaptive ventilation skins"),
    ("NZS09", "S1", "Fixed external shading"), ("NZS10", "S2", "Adjustable shading"),
    ("NZS11", "S2", "Daylighting and light shelves"), ("NZS12", "S2", "Low solar-gain glazing"),
    ("NZS13", "S2", "Insulation"), ("NZS14", "S2", "Airtightness"),
    ("NZS15", "S2", "Thermal mass"), ("NZS16", "S2", "Cool roofing"),
    ("NZS17", "S2", "Green roofs and facades"), ("NZS18", "S2", "High-efficiency cooling"),
    ("NZS19", "S2", "Efficient lighting and controls"), ("NZS20", "S2", "On-site renewables"),
    ("NZS21", "S3", "Low-carbon cement and concrete"), ("NZS22", "S3", "Earth-based construction"),
    ("NZS23", "S3", "Timber and bio-based materials"), ("NZS24", "S3", "Structural material optimisation"),
    ("NZS25", "S3", "Locally sourced materials"), ("NZS26", "S4", "Cradle-to-grave assessment"),
    ("NZS27", "S4", "Whole-life carbon accounting"), ("NZS28", "S4", "Embodied carbon benchmarking"),
    ("NZS29", "S4", "End-of-life scenario modelling"), ("NZS30", "S4", "Nearly net-zero intermediate target"),
]

# The ten DEMATEL factors: six circular principle clusters and four strategy groups
DEMATEL_FACTORS = {**{f"CE-{k}": v for k, v in CE_CLUSTERS.items()}, **NZS_GROUPS}

# Wu and Lee (2007) linguistic scale as triangular fuzzy numbers (l, m, r)
LINGUISTIC_SCALE = {
    0: ("No influence", (0.00, 0.00, 0.25)),
    1: ("Very low influence", (0.00, 0.25, 0.50)),
    2: ("Low influence", (0.25, 0.50, 0.75)),
    3: ("High influence", (0.50, 0.75, 1.00)),
    4: ("Very high influence", (0.75, 1.00, 1.00)),
}
