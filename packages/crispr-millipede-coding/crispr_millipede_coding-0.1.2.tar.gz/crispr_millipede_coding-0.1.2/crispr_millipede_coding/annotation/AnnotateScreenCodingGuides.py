from typing import List, Optional
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from multiprocessing import Pool

class GeneAnnotations:
    '''Class for processing and storing the annotations of provided genes relevant for the screen'''
    def __init__(self,  gene_symbol_list: List[str], reference_annotation_fn: str="/data/molpath/genomes/hg38/hg38.gtf"):
        self.gene_symbol_list = gene_symbol_list
        self.reference_annotation_fn = reference_annotation_fn
        
        self.annotation_gtf_df = pd.read_table(reference_annotation_fn, header=None)
        # Extract gene_id from annotation, add to new column
        def get_geneid_from_info(info):
            gene_id_start = info.find("gene_id") + len("gene_id") + 2
            gene_id_end = info.find(";")-1
            return info[gene_id_start:gene_id_end]
        self.annotation_gtf_df[9] = self.annotation_gtf_df.iloc[:, 8].apply(get_geneid_from_info)

        # Extract exon_number from annotation, add to new column
        def get_exonnumber_from_info(info):
            exon_num_index = info.find("exon_number")
            if exon_num_index != -1:
                exon_num_start = exon_num_index+len("exon_number")+2
                exon_num_sub = info[exon_num_start:exon_num_start+4]
                exon_num_end = exon_num_sub.find("\"")
                return int(exon_num_sub[:exon_num_end])
        self.annotation_gtf_df[10] = self.annotation_gtf_df.iloc[:, 8].apply(get_exonnumber_from_info)
        
        self.annotation_gtf_gene_df_dict = {gene_symbol:self.annotation_gtf_df[self.annotation_gtf_df.iloc[:, 9]==gene_symbol] for gene_symbol in gene_symbol_list}
        self.gene_coordinates_dict = {gene_symbol: self.__get_sequence_annotations__(annotation_gtf_gene_df) for gene_symbol, annotation_gtf_gene_df in self.annotation_gtf_gene_df_dict.items()}
        
        
        
    def __get_sequence_annotations__(self, gene_annotation_table):
        if gene_annotation_table.iloc[0,6] == "-":
            first_exon = gene_annotation_table[(gene_annotation_table.iloc[:,2] == "exon") & (gene_annotation_table.iloc[:,10] == np.max(gene_annotation_table.iloc[:,10]))]
            start_codon = gene_annotation_table[gene_annotation_table.iloc[:, 2]=="start_codon"]

            last_exon = gene_annotation_table[(gene_annotation_table.iloc[:,2] == "exon") & (gene_annotation_table.iloc[:,10] == np.min(gene_annotation_table.iloc[:,10]))]
            stop_codon = gene_annotation_table[gene_annotation_table.iloc[:, 2]=="stop_codon"]

            utr5_left = start_codon.iloc[0,4]+1
            utr5_right = first_exon.iloc[0,4] + 21 # Adding 21nt buffer for guides just outside border

            utr3_left = last_exon.iloc[0,3] - 21 # Adding 21nt buffer for guides just outside border
            utr3_right = stop_codon.iloc[0,3]-1

            sequence_left = stop_codon.iloc[0,3]
            sequence_right = start_codon.iloc[0,4]

            return {"utr5": (gene_annotation_table.iloc[0,0], utr5_left, utr5_right), "utr3": (gene_annotation_table.iloc[0,0], utr3_left, utr3_right), "sequence": (gene_annotation_table.iloc[0,0], sequence_left, sequence_right)}
        elif gene_annotation_table.iloc[0,6] == "+":
            first_exon = gene_annotation_table[(gene_annotation_table.iloc[:,2] == "exon") & (gene_annotation_table.iloc[:,10] == np.min(gene_annotation_table.iloc[:,10]))]
            start_codon = gene_annotation_table[gene_annotation_table.iloc[:, 2]=="start_codon"]

            last_exon = gene_annotation_table[(gene_annotation_table.iloc[:,2] == "exon") & (gene_annotation_table.iloc[:,10] == np.max(gene_annotation_table.iloc[:,10]))]
            stop_codon = gene_annotation_table[gene_annotation_table.iloc[:, 2]=="stop_codon"]

            utr5_left = first_exon.iloc[0,3] - 21 
            utr5_right =  start_codon.iloc[0,3]-1 # Adding 21nt buffer for guides just outside border

            utr3_left = stop_codon.iloc[0,4]+1
            utr3_right = last_exon.iloc[0,4] + 21 # Adding 21nt buffer for guides just outside border

            sequence_left = start_codon.iloc[0,3]
            sequence_right = stop_codon.iloc[0,4]

            return {"utr5": (gene_annotation_table.iloc[0,0], utr5_left, utr5_right), "utr3": (gene_annotation_table.iloc[0,0], utr3_left, utr3_right), "sequence": (gene_annotation_table.iloc[0,0], sequence_left, sequence_right)}
        else:
            raise Exception("Not implemented for strand " + str(gene_annotation_table.iloc[0,6]))
            
    def __repr__(self):
        return str(self.gene_symbol_list) + ";" + str(self.reference_annotation_fn)
    

class GenomeChromosomeSequences:
    def __init__(self, reference_fasta_fn: str, valid_chromosomes: List[str] = None, cores:int=1):
        self.reference_fasta_fn = reference_fasta_fn
        '''
            Read in reference genome
        '''
        if valid_chromosomes is None:
            valid_chromosomes = ["chr" + str(i) for i in range(1,23)] + ["chrX", "chrY"]
        
        '''
            TODO 20220723 Unsure if parallelization is working
        '''
        assert cores > 0, "Cores must be at least 1"
        if cores == 1:
            with open(self.reference_fasta_fn,'r') as reference_fasta_file:
                self.chromosome_sequences_dict = dict([GenomeChromosomeSequences.record_elements(record) for record in SeqIO.parse(reference_fasta_file, "fasta") if record.id in valid_chromosomes])
        else:
            with open(self.reference_fasta_fn,'r') as reference_fasta_file, Pool(cores) as pool:
                self.chromosome_sequences_dict = dict(pool.map(
                    GenomeChromosomeSequences.record_elements,
                    (record for record in SeqIO.parse(reference_fasta_file, "fasta") if record.id in valid_chromosomes),
                    chunksize=1
                ))
    
    @staticmethod
    def record_elements(record): 
        return (record.id, record.seq)
    

class ScreenAnnotationFunctions:
    @staticmethod
    def get_coord_annotation(screenGeneAnnotations: GeneAnnotations, guide_chrom, editsite):
        for gene, seq_annotations in screenGeneAnnotations.gene_coordinates_dict.items():
            for element, element_coordinates in seq_annotations.items():
                annotation_id = gene + "_" + element

                element_chrom = element_coordinates[0]
                element_start = element_coordinates[1]
                element_end = element_coordinates[2]

                if (guide_chrom == element_chrom) and (editsite >= element_start) and (editsite <= element_end):
                    return annotation_id
                
    @staticmethod
    def get_coords(genomeChromosomeSequences: GenomeChromosomeSequences, protospacer):
        indices = []
        for chrom in genomeChromosomeSequences.chromosome_sequences_dict:
            coords = [(chrom, "+", match.start(), match.end(), ScreenGuideSet.get_coord_annotation(chrom, match.start()+6)) for match in re.finditer(protospacer, str(genomeChromosomeSequences.chromosome_sequences_dict[chrom]))]
            if len(coords) == 0:
                coords = [(chrom, "-", match.start(), match.end(), ScreenGuideSet.get_coord_annotation(chrom, match.end()-6)) for match in re.finditer(str(Seq(protospacer).reverse_complement()), str(genomeChromosomeSequences.chromosome_sequences_dict[chrom]))]
                if len(coords) == 0:
                    continue
                else:
                    indices.extend(coords)
            else:
                indices.extend(coords)

        return indices

    # Ideal for identifying unintentional matches outside of annotated regions
    @staticmethod
    def annotate_guides(guide_sequences_series: pd.Series, cores=1):
        with Pool(cores) as pool:
            guide_sequences_annotations = pool.map(
                ScreenGuideSet.get_coords,
                guide_sequences_series.values)
            
        return guide_sequences_annotations
    
    @staticmethod
    def restrictive_guide_annotation(screenGeneAnnotations: GeneAnnotations, genomeChromosomeSequences: GenomeChromosomeSequences, protospacer: Seq, buffer = 20, edit_position=6):
        for gene, seq_annotations in screenGeneAnnotations.gene_coordinates_dict.items():
            for element, element_coordinates in seq_annotations.items():
                annotation_id = gene + "_" + element

                element_chrom = element_coordinates[0]
                element_start = element_coordinates[1]
                element_end = element_coordinates[2]
                element_start_buffered = element_start - buffer
                element_end_buffered = element_end - buffer
                
                element_sequence_buffered = genomeChromosomeSequences.chromosome_sequences_dict[element_chrom][element_start_buffered:element_end_buffered]
                coordinate = element_sequence_buffered.find(protospacer)
                if coordinate >= 5:
                    return (gene, element, "+")
                else:
                    coordinate = element_sequence_buffered.reverse_complement().find(protospacer)
                    if coordinate >= 5:
                        return (gene, element, "-")
        return ("None", "None", None)
    
    @staticmethod
    def is_editable(guide, editing_window_start = 2, editing_window_end = 9, base="A"):
        return base in guide[editing_window_start:editing_window_end].upper()


class ScreenGuideSet:
    '''Object containing the guide set'''
    
    def __init__(self, guide_sequence_series: pd.Series, editing_window_start: int, editing_window_end: int, base: str, remove_duplicates:bool =True, genome_chromosome_sequences: Optional[GenomeChromosomeSequences] = None):
        self.editing_window_start = editing_window_start
        self.editing_window_end = editing_window_end
        
        '''
            Read in guide sequence whitelist
        '''
        self.guide_sequences_series = self.guide_sequences_series.apply(lambda guide: guide.upper())
        if remove_duplicates:
            self.guide_sequences_series = self.guide_sequences_series[~self.guide_sequences_series.duplicated()]
        
        self.guide_sequences_is_editable = self.guide_sequences_series.apply(ScreenAnnotationFunctions.is_editable, args=(self.editing_window_start, self.editing_window_end, base,))
        self.guide_sequences_series.index = self.guide_sequences_series
        self.guide_sequences_is_editable.index = self.guide_sequences_series
        
        print("{} number of guides".format(self.guide_sequences_series.shape[0]))

        if genome_chromosome_sequences is not None:
            guides_sequences_gene_annotated, guides_sequences_element_annotated, guides_sequences_strand_annotated = zip(*[ScreenAnnotationFunctions.restrictive_guide_annotation(genome_chromosome_sequences, protospacer) for protospacer in self.guide_sequences_series])
            self.guides_sequences_gene_annotated = pd.Series(guides_sequences_gene_annotated, index = self.guide_sequences_series)
            self.guides_sequences_element_annotated = pd.Series(guides_sequences_element_annotated, index = self.guide_sequences_series)
            self.guides_sequences_strand_annotated = pd.Series(guides_sequences_strand_annotated, index = self.guide_sequences_series)
    
