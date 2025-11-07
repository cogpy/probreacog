/// @addtogroup poincare
/// @{

/////////////////////////////////////////////////////////////////////////////
/// @file AbstractPdeSection.h
///
/// @author Daniel Wilczak
/////////////////////////////////////////////////////////////////////////////

// Copyright (C) 2000-2013 by the CAPD Group.
//
// Distributed under the terms of the GNU General Public License.
// Consult  http://capd.ii.uj.edu.pl/ for details.

#ifndef _CAPD_PDES_ABSTRACT_PDE_SECTION_H_
#define _CAPD_PDES_ABSTRACT_PDE_SECTION_H_

#include <string>
#include "capd/dynset/AbstractSet.h"
#include "capd/diffAlgebra/Hessian.h"
#include "capd/diffAlgebra/Jet.h"
#include "capd/poincare/AbstractSection.h"

namespace capd{

/// This namespace contains classes that compute Poincare Maps and Time Maps for pdes
namespace pdes{

template<class VectorT, class MatrixT>
class PdeAbstractSection
{
public:
  typedef MatrixT MatrixType;
  typedef VectorT VectorType;
  typedef typename MatrixType::RowVectorType FiniteVectorType;
  typedef typename MatrixType::ScalarType ScalarType;
  typedef typename VectorType::size_type size_type;             ///< integral type used to index containers (vectors, matrices, etc)
  typedef capd::dynset::AbstractSet<FiniteVectorType> Set;   ///< type of abstract base class for all sets

  typedef capd::diffAlgebra::Hessian<ScalarType,FiniteVectorType::csDim,FiniteVectorType::csDim> HessianType;
  typedef capd::diffAlgebra::Jet<MatrixT,0> JetType;

  virtual ScalarType operator() (const VectorType& v) const = 0;     ///< evaluates function at a given vector
  virtual VectorType gradient(const VectorType& u) const = 0;        ///< returns gradient of the function computed at vector u
  virtual ScalarType gradientByVector(const VectorType& x, const VectorType& u) const = 0;

  virtual const capd::poincare::AbstractSection<MatrixType>& getProjection(size_type) const = 0;
  /** This is very important function.
      If it returns true, class PoincareMap delegates computation of value of section(set) to the section.
      Otherwise it is assumed that the set has more information to compute value of section(set) in most optimal way.
      This is quite natural as the set knows its own representation.
      This function returns true for instance if the PoincareSection is given by x_i=c, where x_i is i-th coordinate and c is constant.
  */
  virtual bool isSpecialSection() const{
    return false;
  }

  /** This function computes value of section function on a given set.*/
  virtual ScalarType evalAt(const Set& set) const
  {
    throw std::logic_error("AbstractPdeSection::evalAt not implemented");
  }

  /** computes gradient of return time
      @param[in] derivativeOfFlow - solution to first variational equation computed at return time
      @param[in] gradientOnPx - gradient of function that defines Poincare section evaluated at Px
      @param[in] denominator - scalar product of vector field evaluated at Px and gradientOnPx
      @param[out] result - computed gradient of return time
  */
  virtual void computeDT(
          const MatrixType& derivativeOfFlow,
          const VectorType& gradientOnPx,
          const ScalarType& denominator,
          VectorType& result
     ) const
  {
    throw std::logic_error("AbstractPdeSection::computeDT not implemented");
  }

  /** Simultaneous computation of gradient of return time and derivative of Poincare Map dP.
      @param[in] Px - value of Poincare map
      @param[in] derivativeOfFlow - solution to first variational equation computed at return time
      @param[out] dT - computed gradient of return time
      @param[in] returnTime - enclosure of return time
      @note returnTime must be specified for nonautonomous flows only. Otherwise, default value 0 is valid.
  */
  virtual MatrixType computeDP(
          const VectorType& Px,
          const MatrixType& derivativeOfFlow,
          const VectorType& fieldOnPx,
          VectorType& dT
     ) const
  {
    throw std::logic_error("AbstractPdeSection::computeDP not implemented");
  }

  /** Simultaneous computation of first and second Taylor coefficients of return time and Poincare map.
      @param[in] Px - value of Poincare map
      @param[in] derivativeOfFlow - solution to first variational equation computed at return time
      @param[in] hessianOfFlow - solution to first variational equation computed at return time
      @param[in] fieldOnPx - vector field evaluated at (t(Px),Px)
      @param[out] DP - computed derivative of Poincare map
      @param[out] D2P - computed second order Taylor coefficients of Poincare map
      @param[out] dT - computed gradient of return time
      @param[out] d2T - computed second order Taylor coefficients of return time
      @param[in] returnTime - return time to the section
      @note all input and output parameters are Taylor coefficients, not derivatives!
  */
  virtual void computeDP(
          const VectorType& Px,
          const MatrixType& derivativeOfFlow,
          const HessianType& hessianOfFlow,
          const VectorType& fieldOnPx,
          const VectorType& d2Phidt2,
          const MatrixType& derOfVectorFieldOnPx,
          MatrixType& DP,
          HessianType& D2P,
          VectorType& dT,
          MatrixType& d2T
      ) const
  {
    throw std::logic_error("AbstractPdeSection::computeD2P not implemented");
  }
}; // end of template AbstractSection

}} // namespace capd::poincare

#endif  /* _CAPD_POINCARE_ABSTRACT_SECTION_H_ */

/// @}
