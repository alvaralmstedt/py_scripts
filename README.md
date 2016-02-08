#py_scripts
misc short python scripts!

### fasta_capitals.py

Translates a fasta file containing mixed lowercase and uppercase nucleotides or amino acids into either only uppercase or only lowecase.

    Usage: fasta_capitals.py <infile> <action>

Actions: u/U for translation into uppercase. l/L for translation into lowercase.

### blast_to_gff.py

Converts a custom blast result or minimal bed file into a minimal gff file. Only accound for name, start, stop and orientation.

    Usage: blast_to_gff.py <infile> <outfile.gff>
