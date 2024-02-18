import pathlib

import anndata
import numpy as np
import pandas as pd
import xarray as xr
import zarr
from numcodecs import Blosc
from tqdm import tqdm


def _chrom_sizes_to_chorm_offset_table(chrom_sizes):
    # chrom offset table
    chrom_sizes = chrom_sizes.sort_index()
    chrom_offset_table = pd.DataFrame({"size": chrom_sizes, "global_end": chrom_sizes.cumsum()})
    chrom_offset_table["global_start"] = chrom_offset_table["global_end"] - chrom_sizes
    chrom_offset_table = chrom_offset_table[["global_start", "global_end", "size"]].copy()
    chrom_offset_table.index.name = "chrom"
    chrom_offset_table.columns.name = "offset_value"
    return chrom_offset_table


def _get_bedpe_fragments(
    bedpe_chunk,
    chr1,
    start1,
    chr2,
    end2,
    mapq_col,
    min_mapq,
    strand1,
    strand2,
    barcode_col,
    use_chroms,
    adjust_tn5,
):
    flags = []
    if use_chroms is not None:
        flags.append(bedpe_chunk[chr1].isin(use_chroms))
    if chr2 is not None:
        flags.append(bedpe_chunk[chr1] == bedpe_chunk[chr2])
    if mapq_col is not None:
        flags.append(bedpe_chunk[mapq_col] >= min_mapq)
    if strand1 is not None and strand2 is not None:
        flags.append(bedpe_chunk[strand1] != bedpe_chunk[strand2])

    bedpe_chunk = bedpe_chunk.iloc[np.all(flags, axis=0)]

    if adjust_tn5:
        r1_is_pos_strand = bedpe_chunk[strand1] == "+"
        r1_start_adj = np.where(r1_is_pos_strand, -5, 4)
        bedpe_chunk.iloc[:, start1] += r1_start_adj
        r2_end_adj = np.where(r1_is_pos_strand, 4, -5)
        bedpe_chunk.iloc[:, end2] += r2_end_adj

    frag_bed = bedpe_chunk.iloc[:, [chr1, start1, end2, barcode_col]].copy()
    return frag_bed


def fragments_to_cutsite_zarr(
    fragments_path,
    chrom_sizes_path,
    output_zarr_path,
    barcode_prefix=None,
    chrom_col=0,
    start_col=1,
    end_col=2,
    barcode_col=3,
    chrom2_col=None,
    end2_col=None,
    strand_col=None,
    strand2_col=None,
    mapq_col=None,
    min_mapq=30,
    format="bed",
    adjust_tn5=False,
    chunk_size=20000000,
):
    """
    Extracts the unique cut sizes for each cell barcode and stores them in a zarr store.

    Parameters
    ----------
    fragments_path : str
        Path to the fragments file. The file should be a tab-separated file with columns
        for chromosome, start position, end position, and barcode.
    chrom_sizes_path : str
        Path to the chromosome sizes file. The file should be a tab-separated file with
        two columns: chromosome name and size.
    output_zarr_path : str
        Path to the output zarr store.
    barcode_prefix : str, optional
        Prefix to add to the barcode to make it globally unique across multiple datasets. Default is None.
    chrom_col : int, optional
        Column index for the chromosome in the fragments file. Default is 0.
    start_col : int, optional
        Column index for the start position in the fragments file. Default is 1.
    end_col : int, optional
        Column index for the end position in the fragments file. Default is 2.
    barcode_col : int, optional
        Column index for the barcode in the fragments file. Default is 3 for bed format and 6 for bedpe format.
    chrom2_col : int, optional
        Column index for the second chromosome in the bedpe fragments file. If format is bedpe, this will be set to 3.
        Default is None.
    end2_col : int, optional
        Column index for the second end position in the bedpe fragments file. If format is bedpe, this will be set to 5.
        Default is None.
    strand_col : int, optional
        Column index for the strand in the bedpe fragments file. If format is bedpe, this will be set to 8. Default is None.
    strand2_col : int, optional
        Column index for the second strand in the bedpe fragments file. If format is bedpe, this will be set to 9.
        Default is None.
    mapq_col : int, optional
        Column index for the mapping quality in the bedpe fragments file. If format is bedpe, this will be set to 7.
        Default is None.
    min_mapq : int, optional
        Minimum mapping quality for the fragments. Default is 30.
    format : str, optional
        Format of the fragments file. Default is "bed". Other option is "bedpe".
    adjust_tn5 : bool, optional
        Adjust the TN5 positions for the fragments. Default is False.
    chunk_size : int, optional
        Chunk size for the zarr store. Default is 20,000,000.

    Returns
    -------
    None
    """
    # check if zarr store already exists and there is a success flag
    success_flag = pathlib.Path(output_zarr_path) / ".success"
    if pathlib.Path(output_zarr_path).exists():
        if success_flag.exists():
            print(f"Zarr store already exists at {output_zarr_path}")
            return

    # set default column indices for bedpe
    if format == "bedpe":
        chrom2_col = 3
        end2_col = 5
        barcode_col = 6
        mapq_col = 7
        strand_col = 8
        strand2_col = 9
        print("Using bedpe format from BEDTOOLS")
        if adjust_tn5:
            print("Adjusting TN5 positions")
    if chrom2_col is not None:
        bedpe = True

    zarr.storage.default_compressor = Blosc()

    chrom_sizes = pd.read_csv(chrom_sizes_path, header=None, sep="\t", index_col=0).squeeze()
    chrom_offset_table = _chrom_sizes_to_chorm_offset_table(chrom_sizes)

    # process fragments
    frag_chunks = pd.read_csv(fragments_path, chunksize=1000000, header=None, sep="\t")
    cur_barcode_id = 0
    barcode_id_map = {}
    records = {}
    for chunk in tqdm(frag_chunks):
        if bedpe:
            # process bedpe and adjust for TN5, return the fragment bed
            chunk = _get_bedpe_fragments(
                bedpe_chunk=chunk,
                chr1=chrom_col,
                start1=start_col,
                chr2=chrom2_col,
                end2=end2_col,
                mapq_col=mapq_col,
                min_mapq=min_mapq,
                strand1=strand_col,
                strand2=strand2_col,
                barcode_col=barcode_col,
                use_chroms=chrom_offset_table.index,
                adjust_tn5=adjust_tn5,
            )

        for barcode, barcode_df in chunk.groupby(barcode_col):
            if barcode in barcode_id_map:
                barcode_idx = barcode_id_map[barcode]
                exist = True
            else:
                barcode_idx = cur_barcode_id
                cur_barcode_id += 1
                barcode_id_map[barcode] = barcode_idx
                exist = False

            use_frags_df = barcode_df[barcode_df[chrom_col].isin(chrom_offset_table.index)].iloc[
                :, [chrom_col, start_col, end_col]
            ]
            global_cutsites = (
                use_frags_df.iloc[:, 1:]
                + use_frags_df.iloc[:, 0].map(chrom_offset_table["global_start"]).values[:, None]
            )
            global_cutsites = np.sort(np.unique(global_cutsites.values.ravel()))

            if exist:
                cur_cutsites = records[barcode_idx]
                new_cutsites = np.sort(np.unique(np.concatenate([cur_cutsites, global_cutsites])))
                records[barcode_idx] = new_cutsites

            else:
                records[barcode_idx] = global_cutsites

    # prepare an empty zarr store
    total_cutsites_count = sum(v.size for v in records.values())
    final_array = xr.DataArray(
        np.zeros((total_cutsites_count, 2), dtype="uint32"),
        dims=["site", "value"],
        coords={"value": ["barcode", "global_pos"]},
    )
    final_array = final_array.chunk({"site": chunk_size, "value": "1"})
    final_ds = xr.Dataset({"cutsite": final_array})
    # apply barcode prefix if provided
    if barcode_prefix is not None:
        barcode_id_map = {f"{barcode_prefix}:{k}": v for k, v in barcode_id_map.items()}
    final_ds["barcode_map"] = xr.DataArray(pd.Series(barcode_id_map), dims="barcode")
    final_ds["chrom_offset"] = xr.DataArray(chrom_offset_table, dims=["chrom", "offset_value"])
    for k in list(final_ds.coords.keys()):
        v = final_ds.coords[k]
        final_ds.coords[k] = v.astype(str)
        final_ds.coords[k].encoding = {"chunks": (v.size,)}
    final_ds.to_zarr(output_zarr_path, mode="w")

    # write the cutsites in large chunks
    final_array = zarr.open_array(f"{output_zarr_path}/cutsite/")
    mat_records = []
    temp_site_counts = chunk_size
    cur_start = 0
    for barcode, cutsites in records.items():
        mat = np.zeros((cutsites.size, 2), dtype="uint32")
        mat[:, 0] = barcode
        mat[:, 1] = cutsites
        mat_records.append(mat)
        temp_site_counts -= cutsites.size

        if (temp_site_counts < 0) and len(mat_records) != 0:
            mat_records = np.concatenate(mat_records)
            cur_end = cur_start + mat_records.shape[0]
            final_array[cur_start:cur_end, :] = mat_records

            cur_start = cur_end
            mat_records = []
            temp_site_counts = chunk_size

    # final chunk
    if len(mat_records) != 0:
        mat_records = np.concatenate(mat_records)
        cur_end = cur_start + mat_records.shape[0]
        final_array[cur_start:cur_end, :] = mat_records

    # write a success flag to the zarr store
    success_flag.touch()
    return


def adata_cutsites_to_zarr(adata_path, output_zarr_path, barcode_prefix=None, chunk_size=20000000):
    """
    Converts the insertion matrix (sparse format) from SnapATAC2 anndata object into a zarr store.

    Parameters
    ----------
    adata_path : str
        Path to the anndata object.
    output_zarr_path : str
        Path to the output zarr store.
    barcode_prefix : str, optional
        Prefix to add to the barcode to make it globally unique across multiple datasets. Default is None.
    chunk_size : int, optional
        Chunk size for the zarr store. Default is 20,000,000.

    Returns
    -------
    None
    """
    success_flag = pathlib.Path(output_zarr_path) / ".success"
    if pathlib.Path(output_zarr_path).exists():
        if success_flag.exists():
            print(f"Zarr store already exists at {output_zarr_path}")
            return

    adata = anndata.read_h5ad(adata_path)

    assert "insertion" in adata.obsm_keys(), "insertion matrix not found in adata.obsm"
    assert "reference_sequences" in adata.uns_keys(), "reference_sequences not found in adata.uns"

    # prepare chrom offset table directly from adata.uns
    chrom_sizes = adata.uns["reference_sequences"].set_index("reference_seq_name").squeeze()
    chrom_offset_table = _chrom_sizes_to_chorm_offset_table(chrom_sizes)

    # turn insertion mat into coo like format for zarr store
    insertions = adata.obsm["insertion"]
    barcode_id_map = {b: i for i, b in enumerate(adata.obs_names)}

    coo = insertions.tocoo()
    zarr_data = np.array([coo.row, coo.col], dtype="uint32").T

    # prepare the zarr store
    final_array = xr.DataArray(
        zarr_data,
        dims=["site", "value"],
        coords={"value": ["barcode", "global_pos"]},
    )
    final_array = final_array.chunk({"site": chunk_size, "value": "1"})
    final_ds = xr.Dataset({"cutsite": final_array})
    # apply barcode prefix if provided
    if barcode_prefix is not None:
        barcode_id_map = {f"{barcode_prefix}:{k}": v for k, v in barcode_id_map.items()}
    final_ds["barcode_map"] = xr.DataArray(pd.Series(barcode_id_map), dims="barcode")
    final_ds["chrom_offset"] = xr.DataArray(chrom_offset_table, dims=["chrom", "offset_value"])
    for k in list(final_ds.coords.keys()):
        v = final_ds.coords[k]
        final_ds.coords[k] = v.astype(str)
        final_ds.coords[k].encoding = {"chunks": (v.size,)}
    final_ds.to_zarr(output_zarr_path, mode="w")

    # write a success flag to the zarr store
    success_flag.touch()
    return
