/// @addtogroup pdes
/// @{

/////////////////////////////////////////////////////////////////////////////
/// @file DissipativeVectorField.h
///
/// @author Daniel Wilczak
/////////////////////////////////////////////////////////////////////////////

// Copyright (C) 2008-2016 by the CAPD Group.
//
// Distributed under the terms of the GNU General Public License.
// Consult  http://capd.ii.uj.edu.pl/ for details.

#ifndef _CAPD_PDES_DISSIPATIVEVECTORFIELD_H_
#define _CAPD_PDES_DISSIPATIVEVECTORFIELD_H_

#include <vector>
#include "capd/intervals/lib.h"
#include "capd/vectalg/lib.h"

namespace capd {
namespace pdes {

/**
 * The class provides a common interface for a dissipative vector required by the class PDESolver.
 * Each particular system should inherit and implement abstract methods.
*/
template<class SeriesT>
class DissipativeVectorField {
public:
  // typedef SeriesT SeriesType;
  typedef capd::interval ScalarType;
  typedef SeriesT VectorType;
  typedef capd::IMatrix MatrixType;  

  typedef capd::IVector::size_type size_type;
  typedef std::vector<VectorType> VectorArray;
  typedef std::vector<VectorArray> MatrixArray;

  virtual VectorType operator()(ScalarType h, const VectorType& v) = 0;
  virtual VectorType operator()(ScalarType h, const VectorType& v, MatrixType& DF) = 0;
  virtual MatrixType derivative(ScalarType h, const VectorType& v) = 0;

  /// This function should compute ODE coefficients up to given order at the set a
  virtual void computeODECoefficients(VectorArray& a, size_type order) = 0;

  /// This function should compute ODE coefficients up to given order at the set a
  /// Moreover, block derivative of first group of variables has to be computed.
  virtual void computeODECoefficients(VectorArray& a, MatrixArray&, size_type order) = 0;

  /// This function asserts that the vector field is pointing inside the tail.
  virtual void makeSelfConsistentBound(VectorArray& a) = 0;

  virtual size_type dimension() const = 0;
  virtual size_type firstDissipativeIndex() const = 0;

  virtual void updateTail(VectorType& x, const VectorArray& a, const VectorArray& enc, ScalarType h, size_type p) const = 0;
};

}} // namespace capd::pdes


#endif // _CAPD_PDES_DISSIPATIVEVECTORFIELD_H_

/// @}
