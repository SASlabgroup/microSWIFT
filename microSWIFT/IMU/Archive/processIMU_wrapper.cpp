/* ************************************************************************ */
/*                                                                          */
/*                                                                          */
/* ***********************************************************************  */
/* Include files */
#include "rt_nonfinite.h"
#include "processIMU_emxAPI.h"
#include "processIMU_initialize.h"
#include "processIMU_emxutil.h"
#include "processIMU_types.h"
#include "processIMU.h"
#include "/usr/local/include/boost/python.hpp"
#include "/usr/local/include/boost/python/module.hpp"
#include "/usr/local/include/boost/python/def.hpp"
#include "/usr/local/include/boost/python/extract.hpp"
#include "/usr/local/include/boost/python/numpy.hpp"
#include "/usr/local/include/boost/python/numpy/ndarray.hpp"
#include "/usr/local/include/boost/python/args.hpp"
#include <iostream>
#include <vector>


using namespace boost::python;
namespace np = boost::python::numpy;

/* Function Declarations */
tuple main_processIMU(int nsize, np::ndarray axi, np::ndarray ayi, np::ndarray azi, 
                                 np::ndarray gxi, np::ndarray gyi, np::ndarray gzi, 
                                 np::ndarray mxi, np::ndarray myi, np::ndarray mzi, 
                      double mxoi, double myoi, double mzoi, double Wdi, double fsi)
{

  int i;
  double Hs, Tp, Dp;

  emxArray_real_T *D  = emxCreate_real_T(1, nsize);
  emxArray_real_T *E  = emxCreate_real_T(1, nsize);
  emxArray_real_T *f  = emxCreate_real_T(1, nsize);
  emxArray_real_T *a1 = emxCreate_real_T(1, nsize);
  emxArray_real_T *b1 = emxCreate_real_T(1, nsize);
  emxArray_real_T *a2 = emxCreate_real_T(1, nsize);
  emxArray_real_T *b2 = emxCreate_real_T(1, nsize);
  emxArray_real_T *check = emxCreate_real_T(1, nsize);

  emxInitArray_real_T(&E, 2);
  emxInitArray_real_T(&f, 2);
  emxInitArray_real_T(&a1, 2);
  emxInitArray_real_T(&b1, 2);
  emxInitArray_real_T(&a2, 2);
  emxInitArray_real_T(&b2, 2);
 
  double axsd[nsize];
  double aysd[nsize];
  double azsd[nsize];
  double gxsd[nsize];
  double gysd[nsize];
  double gzsd[nsize];
  double mxsd[nsize];
  double mysd[nsize];
  double mzsd[nsize];

  double* axi_ptr = reinterpret_cast<double*>(axi.get_data()); 
  double* ayi_ptr = reinterpret_cast<double*>(ayi.get_data());
  double* azi_ptr = reinterpret_cast<double*>(azi.get_data());
  double* gxi_ptr = reinterpret_cast<double*>(gxi.get_data());
  double* gyi_ptr = reinterpret_cast<double*>(gyi.get_data());
  double* gzi_ptr = reinterpret_cast<double*>(gzi.get_data());
  double* mxi_ptr = reinterpret_cast<double*>(mxi.get_data());
  double* myi_ptr = reinterpret_cast<double*>(myi.get_data());
  double* mzi_ptr = reinterpret_cast<double*>(mzi.get_data());



  for (i=0;i<nsize;i++)
  {
    axsd[i]=*(axi_ptr + i);
    aysd[i]=*(ayi_ptr + i);
    azsd[i]=*(azi_ptr + i);
    gxsd[i]=*(gxi_ptr + i);
    gysd[i]=*(gyi_ptr + i);
    gzsd[i]=*(gzi_ptr + i);
    mxsd[i]=*(mxi_ptr + i);
    mysd[i]=*(myi_ptr + i);
    mzsd[i]=*(mzi_ptr + i);
  }


  std::cout<<"NSIZE = "<<nsize<<"\n";
  /*
  std::cout<<"AXS,AYS,AZS,GXS,GYS,GZS,MXS,MYS,MZS,MXoS,MYoS,MZoS "<<"\n";
  for (i=0;i<nsize;i++){
     std::cout<<axsd[i]<<" ";
     std::cout<<aysd[i]<<" ";
     std::cout<<azsd[i]<<" ";
     std::cout<<gxsd[i]<<" ";
     std::cout<<gysd[i]<<" ";
     std::cout<<gzsd[i]<<" ";
     std::cout<<mxsd[i]<<" ";
     std::cout<<mysd[i]<<" ";
     std::cout<<mzsd[i]<<" ";
  }
  */
  /* std::cout<<"entering processIMU"; */
  processIMU(axsd, aysd, azsd, gxsd, gysd, gzsd, mxsd, mysd, mzsd, mxoi, myoi, mzoi, Wdi, fsi, &Hs, &Tp, &Dp, E, f, a1, b1, a2, b2, check);
  /* std::cout<<"out of processIMU"; */
  
  nsize = 42;

  boost::python::tuple shape = boost::python::make_tuple(nsize, 1);
  np::dtype dtype = np::dtype::get_builtin<double>();
  np::ndarray Eo = np::zeros(shape, dtype);
  np::ndarray fo = np::zeros(shape, dtype);
  np::ndarray ao1 = np::zeros(shape, dtype);
  np::ndarray bo1 = np::zeros(shape, dtype); 
  np::ndarray ao2 = np::zeros(shape, dtype);
  np::ndarray bo2 = np::zeros(shape, dtype);

  /*std::cout<<"C RESULTS = "<< nsize << "\n";*/
  for (i=0;i<nsize;i++) {
      Eo[i]= E->data[i];
      fo[i]= f->data[i]; 
      ao1[i]= a1->data[i];
      bo1[i]= b1->data[i];
      ao2[i]= a2->data[i];
      bo2[i]= b2->data[i];
      std::cout<< f->data[i]<<" ";
  };
  return make_tuple(Hs, Tp, Dp, Eo, fo, ao1, bo1, ao2, bo2);

};


/* Define your module name within BOOST_PYTHON_MODULE */
BOOST_PYTHON_MODULE(processIMU_lib) {

  /* Initialise np */
  Py_Initialize();
  np::initialize();
  def("main_processIMU",main_processIMU);
};

