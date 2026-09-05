# -*- coding: utf-8 -*-
CLARO = """    --ground:      #FBFAF7;
    --surface:     #F3F1EC;
    --sunken:      #EAE7E0;
    --ink:         #191B1F;
    --ink-soft:    #3D4149;
    --muted:       #5F636B;
    --faint:       #6C7079;
    --rule:        #D9D5CC;
    --rule-firm:   #BFBAAE;
    --rule-soft:   #E6E2DA;
    --accent:      #33477E;
    --accent-soft: #E1E5F1;
    --warn:        #8A5722;
    --warn-soft:   #F2E7D8;
    --good:        #37613F;
    --good-soft:   #E0EBE1;
    --danger:      #A3352B;
    --danger-soft: #F6E6E3;"""

ESCURO = """    --ground:      #16171A;
    --surface:     #1D1F23;
    --sunken:      #24262B;
    --ink:         #E9E6E0;
    --ink-soft:    #C4C2BD;
    --muted:       #94979E;
    --faint:       #8A8D94;
    --rule:        #34373D;
    --rule-firm:   #454A52;
    --rule-soft:   #2A2D32;
    --accent:      #97AAE2;
    --accent-soft: #23283A;
    --warn:        #D3A163;
    --warn-soft:   #33291B;
    --good:        #83B78D;
    --good-soft:   #1E2A20;
    --danger:      #E07A6E;
    --danger-soft: #2E1E1C;"""

FONTES = """    --serif: Charter, "Bitstream Charter", "Iowan Old Style", "Source Serif Pro", Cambria, Georgia, serif;
    --sans: "Segoe UI", Inter, system-ui, -apple-system, sans-serif;
    --mono: "Cascadia Mono", "JetBrains Mono", ui-monospace, Consolas, "SF Mono", monospace;

    --measure: 66ch;"""

def bloco(alias=""):
    """A folha de tokens comum as paginas da oficina."""
    a = ("\n\n    /* nomes proprios desta pagina, apontando para o sistema */\n" + alias) if alias else ""
    return (":root {\n%s\n\n%s%s\n  }\n\n"
            "  @media (prefers-color-scheme: dark) {\n    :root:not([data-theme=\"light\"]) {\n%s\n    }\n  }\n\n"
            "  :root[data-theme=\"dark\"] {\n%s\n  }\n\n"
            "  :root[data-theme=\"light\"] {\n%s\n  }" ) % (
        CLARO, FONTES, a,
        ESCURO.replace("\n    ", "\n      "),
        ESCURO, CLARO)
