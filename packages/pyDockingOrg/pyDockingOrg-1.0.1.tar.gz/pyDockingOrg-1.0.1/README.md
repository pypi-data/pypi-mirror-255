# smallworld_api2.1
Rewritten version of Matteo Ferla's unofficial python API to SmallWorld (https://github.com/matteoferla/Python_SmallWorld_API)

Please make sure you are allowed to use this interface in the same way that you'd do for Matteo Ferla's API. It interacts with https://sw.docking.org/. 

Updates:
 - Callback-driven requests
 - Threading for handling volume search
 - Default 3-attempt retry strategy to tackle the random HTTP 502 

This version is not thread safe. Only one process can use this class at a time. 

```python
with Enamine() as enamine:
    mols = enamine.search_smiles(
        ['O=C(C)Oc1ccccc1C(=O)O', 'C=C(Cl)CNC(=O)C1(CC)CCC1'], 
        remove_duplicates=True)
    print(mols)
```

Please note that https://sw.docking.org/ now provides a new REST API which should be usd instead. This version should be updated to it. The new interface sends results using a single query (instead of two that we use here with the Hit List IDs), and also alows querying multiple Smiles in one go. 