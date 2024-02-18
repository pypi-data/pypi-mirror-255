#%% Import
import h5py
import collections.abc
import re

#%% Define Class



class StoreSetup:
  def __init__(self, fileName: str = "") -> None:
    self.fileName = fileName


  def createFile(self) -> None:
    with h5py.File(f"{self.fileName}.hdf5", "w") as hf:
      hf.create_group("info")
      hf.create_group("data")
      hf.create_group("outputSignal")
      hf.create_group("postProc")

  def writeInfo(self, infoData) -> None:
    with h5py.File(f"{self.fileName}.hdf5", "a") as hf:
      grp_info = hf["info"]

      for group_name, data in infoData.items():
        if group_name in grp_info:
          del grp_info[group_name]
        grp_name = grp_info.create_group(group_name)

        if isinstance(data, dict):
          names = list(data.keys())

          for name in names:
            items: dict = data[name]
            hfKey = grp_name.create_group(name)

            for key, item in items.items():
              self.__writeInfoEntry(hfKey,item,key)

        else:
          if isinstance(data, tuple):
            value, unit = data
            self.__writeInfoEntry(grp_name,value,"value",unit)


  def __writeInfoEntry(self,grp_name:h5py.File,value,name:str="value",unit:str="") -> None:
    if value is str:
      grp_name.create_dataset(name=name, data=value, dtype=h5py.special_dtype(vlen=str))
    else:
      grp_name.create_dataset(name=name, data=value)

    if unit != "":
      grp_name.create_dataset(name="unit", data=unit, dtype=h5py.special_dtype(vlen=str))


  def writeData(self,iter,dataName,data) -> None:
    with h5py.File(f"{self.fileName}.hdf5", "a") as hf:
      grp_data = hf["data"]
      if isinstance(dataName,collections.abc.Iterable) and not isinstance(dataName,str):
        self.__writeIterable(grp_data,iter,dataName,data)
      else:
        self.__writeSingle(grp_data,iter,dataName,data)


  def writeOutputSignal(self,iter,dataName,data) -> None:
    with h5py.File(f"{self.fileName}.hdf5", "a") as hf:
      grp_data = hf["outputSignal"]
      if isinstance(dataName,collections.abc.Iterable) and not isinstance(dataName,str):
        self.__writeIterable(grp_data,iter,dataName,data)
      else:
        self.__writeSingle(grp_data,iter,dataName,data)


  def writePosProc(self,iter,dataName,data) -> None:
    with h5py.File(f"{self.fileName}.hdf5", "a") as hf:
      grp_postProc = hf["postProc"]

      if f"step-{iter}" in grp_postProc and dataName in grp_postProc[f"step-{iter}"]:
        del grp_postProc[f"step-{iter}"][dataName]

      if isinstance(dataName,collections.abc.Iterable) and not isinstance(dataName,str):
        self.__writeIterable(grp_postProc,iter,dataName,data)
      else:
        self.__writeSingle(grp_postProc,iter,dataName,data)


  def __writeIterable(self,grp,iter,dataName,data) -> None:
    if f"step-{int(iter)}" in grp:
      grp_name = grp[f"step-{int(iter)}"]
    else:
      grp_name = grp.create_group(f"step-{int(iter)}")

    for name, value in zip(dataName,data):
      grp_name.create_dataset(name=name, data=value)


  def __writeSingle(self,grp,iter,name,value) -> None:
    if f"step-{int(iter)}" in grp:
      grp_name = grp[f"step-{int(iter)}"]
    else:
      grp_name = grp.create_group(f"step-{int(iter)}")

    grp_name.create_dataset(name=name, data=value)

  def readData(self,iter="all",storeName="all"):
    with h5py.File(f"{self.fileName}.hdf5", "r") as hf:
      grp = hf["data"]
      if iter == "all":
        return self.__readIter(grp,storeName)
      else:
        return self.__readSingleIter(grp,iter,storeName)
      
  def readInfoValue(self,storeName):
    with h5py.File(f"{self.fileName}.hdf5", "r") as hf:
      grp = hf[f"info/{storeName}"]
      return self.__readSingleStoreName(grp,"value")
    
  def readPostProcInfoValue(self,storeName):
    with h5py.File(f"{self.fileName}.hdf5", "r") as hf:
      grp = hf[f"info/{storeName}"]
      return self.__readSingleStoreName(grp,"value")
      
  def readOutputSignal(self,iter="all",storeName="all"):
    with h5py.File(f"{self.fileName}.hdf5", "r") as hf:
      grp = hf["outputSignal"]
      if iter == "all":
        return self.__readIter(grp,storeName)
      else:
        return self.__readSingleIter(grp,iter,storeName)


  def readPostProc(self,iter="all",storeName="all"):
    with h5py.File(f"{self.fileName}.hdf5", "r") as hf:
      grp = hf["postProc"]
      if iter == "all":
        return self.__readIter(grp,storeName)
      else:
        return self.__readSingleIter(grp,iter,storeName)


  def __readIter(self,grp,storeName):
    returnDict = {}
    for iterStep in grp.keys():
      if iterStep != "info":
        grpIter = grp[iterStep]
        if storeName == "all":
          returnDict[iterStep] = self.__readStoreName(grpIter)
        else:
          returnDict[iterStep] = self.__readSingleStoreName(grpIter,storeName)

    return dict(sorted(returnDict.items(), key=lambda item: int(re.search("(\d+)",item[0]).group(1))))

  def __readSingleIter(self,grp,iter,storeName):
    grp = grp[f"step-{int(iter)}"]
    if storeName == "all":
      return self.__readStoreName(grp)
    else:
      return self.__readSingleStoreName(grp,storeName)

  def __readStoreName(self,grp):
    returnDict={}
    for storeName in grp.keys():
      returnDict[storeName] = grp[storeName][:]
    return returnDict

  def __readSingleStoreName(self,grp,storeName):
    return grp[storeName][()]
















