obsidian_template = '8c308abd4277779a7c8897bfddd40d2dd85f22c3eee2de548aa26923f5021bcd'
ob_sample = '224a09b94b6216227b2ad111d913a7579127dc6f8da2f85d0aeade851a2b7d42'


def verifier():
    import warnings
    from pysidian.utils import compute_hash
    import os
    currentDir = os.path.dirname(os.path.realpath(__file__))

    osset = set(
        [x.split(".")[0] for x in os.listdir(currentDir) 
        if not x.startswith("_") and x.endswith(".zip")]
    )
    globalset = set([x for x in globals().keys() if not x.startswith("_")])
    
    if osset - globalset:
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
        return

    for name, hashcord in globals().items():
        if name.startswith("_"):
            continue

        if not isinstance(hashcord, str):
            continue

        filepath = os.path.join(currentDir, f"{name}.zip")
        
        if not os.path.exists(filepath) or compute_hash(filepath) != hashcord: 
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            warnings.warn("Checksum Mismatch, data may be corrupted or tampered")
            return
     
verifier()