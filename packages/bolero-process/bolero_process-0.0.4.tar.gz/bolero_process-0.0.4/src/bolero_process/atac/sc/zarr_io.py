import numpy as np
import pandas as pd
import xarray as xr
import zarr
from scipy.sparse import csr_matrix


class CutSitesZarr(xr.Dataset):
    """Class to read cutsite zarr file and provide functionality to convert single cell cutsite data to pseudobulk coverage data."""

    def __init__(self, zarr_path) -> None:
        ds = xr.open_zarr(zarr_path)
        super().__init__(data_vars=ds.data_vars, coords=ds.coords, attrs=ds.attrs)

        self.barcode_to_idx = self.ds["barcode_map"].to_pandas()
        self.idx_to_barcode = pd.Series({i: b for b, i in self.barcode_to_idx.items()})
        self.chrom_offsets = self.ds["chrom_offset"].to_pandas()
        self.genome_total_length = self.chrom_offsets["chrom_length"].sum()

    def get_barcodes_idx(self, barcodes):
        """Get the index of the barcodes in the barcode_map."""
        use_barcodes_idx = self.barcode_to_idx[self.barcode_to_idx.index.isin(barcodes)].values
        return use_barcodes_idx

    def _get_barcodes_sites_count(self, barcodes):
        use_idx = self.get_barcodes_idx(barcodes)
        if use_idx.size == 0:
            return pd.Series(dtype=np.uint32)

        # cutsite chunks
        site_chunks = self["cutsite"].chunks[0]
        chunk_boarders = [0] + list(np.cumsum(site_chunks))

        total_cutsites = []
        for _i in range(len(site_chunks)):
            chunk_start = chunk_boarders[_i]
            chunk_end = chunk_boarders[_i + 1]

            # first, select barcode idx bool array
            use_chunk_sites = np.isin(self["cutsite"][chunk_start:chunk_end, 0], use_idx)
            # second, load actual cutsite global positions with the bool array
            use_chunk_cutsites = self["cutsite"][chunk_start:chunk_end, 1][use_chunk_sites].values
            total_cutsites.append(use_chunk_cutsites)

        pos, counts = np.unique(np.concatenate(total_cutsites), return_counts=True)
        counts = pd.Series(counts, index=pos, dtype=np.uint32)
        return counts

    def _sites_count_to_coverage_zarr(self, sites_count, zarr_path, chunk_size=20000000):
        """Convert sites count to coverage."""
        # create a csr matrix with csr_matrix((data, indices, indptr), [shape=(M, N)]) format
        coverage = csr_matrix(
            (sites_count.values, sites_count.index, [0, len(sites_count)]),
            shape=(1, self.genome_total_length),
        )

        # cut the coverage to the chromosome lengths and store in zarr
        root = zarr.group(store=zarr_path, overwrite=True)

        for chrom, (
            global_start,
            global_end,
            _,
        ) in self.chrom_offsets.iterrows():
            chrom_coverage = coverage[global_start:global_end].toarray()
            root.create_dataset(
                f"chrs/{chrom}",
                data=chrom_coverage,
                chunks=chunk_size,
                compressor=zarr.Blosc(cname="zstd", clevel=3, shuffle=zarr.Blosc.SHUFFLE),
            )
        return

    def dump_barcodes_coverage(self, barcodes, zarr_path, chunk_size=20000000):
        """Get the coverage for the barcodes and save to zarr file."""
        sites_count = self._get_barcodes_sites_count(barcodes)
        self._sites_count_to_coverage(sites_count, zarr_path, chunk_size)
        return
