/////////////////////////////////////////////////////////////////////////////
/// @file PdeCurve.h
///
/// @author Daniel Wilczak
/////////////////////////////////////////////////////////////////////////////

// Copyright (C) 2000-2016 by the CAPD Group.
//
// This file constitutes a part of the CAPD library,
// distributed under the terms of the GNU General Public License.
// Consult  http://capd.ii.uj.edu.pl/ for details.

#ifndef _CAPD_PDES_PDECURVE_H_
#define _CAPD_PDES_PDECURVE_H_

#include <stdexcept>
#include "capd/basicalg/TypeTraits.h"
#include "capd/diffAlgebra/CurveInterface.h"
#include "capd/diffAlgebra/ParametricCurve.h"
#include "capd/pdes/GeometricSeries.hpp"

namespace capd{
namespace pdes{
/// @addtogroup pdes
/// @{

/**
 * This class is a data structure for storing of a parametric curve
 * together with first order derivatives with respect to initial point.
 *
 * More precisely, a curve c(t,x) is represented as
 * c(t,x_0) + d/dx c(t,x)(x-x_0) + smallRemainder(t,x)
 *
 * This class provides a member functions for accessing of all coefficients.
 *
 * This class is a basic class for more general Curve.
 */

template<class SeriesT>
class PdeCurve : public capd::diffAlgebra::CurveInterface<capd::IMatrix>,
		 public capd::diffAlgebra::ParametricCurve<capd::IMatrix,SeriesT>
{
public:
  typedef SeriesT VectorType;
  typedef capd::IVector FiniteVectorType;
  typedef capd::IMatrix MatrixType;
  typedef capd::IHessian HessianType;
  typedef capd::IJet JetType;

  typedef typename MatrixType::ScalarType ScalarType;
  typedef typename TypeTraits<ScalarType>::Real Real;
  typedef typename MatrixType::size_type size_type;
  typedef std::vector<VectorType> VectorArray;
  typedef std::vector<VectorArray> MatrixArray;

  PdeCurve(size_type dim, size_type order);
  virtual ~PdeCurve(){}

  PdeCurve& operator=(const PdeCurve& c);

  // implementation of ParametricCurve interface
  virtual VectorType operator()(const ScalarType& h) const {
    VectorType result = this->getRemainderCoefficients()[0];
    FiniteVectorType phi = this->getCoefficientsAtCenter()[0].getExplicitCoefficients();
    FiniteVectorType X = this->getCoefficients()[0].getExplicitCoefficients();
    FiniteVectorType delta = X-phi;
    FiniteVectorType rem = this->getRemainderCoefficients()[this->getOrder()+1].getExplicitCoefficients()*power(h,this->getOrder()+1);
    MatrixType A(this->dimension(),this->dimension());
    this->sumTaylorSeries(phi,getCoefficientsAtCenter(),h,this->getOrder(),this->dimension());
    this->sumTaylorSeries(A,h,this->getOrder(),this->dimension());
    result.setExplicitCoefficients(phi+A*delta+rem);
    return result;
  }
  virtual MatrixType derivative(const ScalarType& h) const {
    throw std::logic_error("PdeCurve::derivative not implemented");
  }
  virtual MatrixType operator[](const ScalarType& h) const { return derivative(h); }


  virtual void setOrder(size_type order); ///< Sets the order of Taylor interpolation
  size_type getOrder() const;             ///< Returns the order of Taylor interpolation
  size_type getAllocatedOrder() const;    ///< Returns maximal allocated order - used to avoid memory reallocation
  size_type dimension() const;            ///< Returns the dimension in which the relevant dynamics is observed.

  void clearCoefficients();             ///< sets all coefficients to zero

  const ScalarType centerCoefficient(size_type i, size_type j) const;
  const ScalarType coefficient(size_type i, size_type j) const;
  const ScalarType remainderCoefficient(size_type i, size_type j) const;
  const ScalarType coefficient(size_type i, size_type j, size_type k) const;
  const ScalarType remainderCoefficient(size_type i, size_type j, size_type k) const;
/*
  ScalarType& centerCoefficient(size_type i, size_type j);
  ScalarType& coefficient(size_type i, size_type j);
  ScalarType& remainderCoefficient(size_type i, size_type j);
  ScalarType& coefficient(size_type i, size_type j, size_type k);
  ScalarType& remainderCoefficient(size_type i, size_type j, size_type k);
*/
  VectorArray& getCoefficientsAtCenter() { return m_coefficientsAtCenter; }
  VectorArray& getCoefficients() { return m_coefficients; }
  VectorArray& getRemainderCoefficients() { return m_remainderCoefficients; }
  MatrixArray& getMatrixCoefficients() { return m_matrixCoefficients; }

  const VectorArray& getCoefficientsAtCenter() const { return m_coefficientsAtCenter; }
  const VectorArray& getCoefficients() const { return m_coefficients; }
  const VectorArray& getRemainderCoefficients() const { return m_remainderCoefficients; }
  const MatrixArray& getMatrixCoefficients() const { return m_matrixCoefficients; }

protected:
  template<class V>
  void sumTaylorSeries(V& x, const VectorArray& c, ScalarType h, int p, size_type dim) const;
  void sumTaylorSeries(MatrixType& A, ScalarType h, int p, size_type dim) const;
  void realloc(size_type dimension);

  VectorArray m_coefficientsAtCenter,
              m_coefficients,
              m_remainderCoefficients;

  MatrixArray m_matrixCoefficients;

  size_type m_order;
};

// ----------------- inline definitions ------------------

template<class SeriesT>
inline typename PdeCurve<SeriesT>::size_type PdeCurve<SeriesT>::getOrder() const{
  return this->m_order;
}

template<class SeriesT>
inline typename PdeCurve<SeriesT>::size_type PdeCurve<SeriesT>::dimension() const{
  return this->m_coefficientsAtCenter[0].dimension();
}

// -----------------------------------------------------------------------------

template<class SeriesT>
inline const typename  PdeCurve<SeriesT>::ScalarType PdeCurve<SeriesT>::centerCoefficient(size_type i, size_type r) const {
  return this->m_coefficientsAtCenter[r][i];
}

template<class SeriesT>
inline const typename PdeCurve<SeriesT>::ScalarType PdeCurve<SeriesT>::coefficient(size_type i, size_type r) const {
  return this->m_coefficients[r][i];
}

template<class SeriesT>
inline const typename PdeCurve<SeriesT>::ScalarType PdeCurve<SeriesT>::remainderCoefficient(size_type i, size_type r) const {
  return this->m_remainderCoefficients[r][i];
}

template<class SeriesT>
inline const typename PdeCurve<SeriesT>::ScalarType PdeCurve<SeriesT>::coefficient(size_type i, size_type j, size_type r) const {
  return this->m_matrixCoefficients[i][r][j];
}

// -----------------------------------------------------------------------------
/*
template<class SeriesT>
inline typename PdeCurve<SeriesT>::ScalarType& PdeCurve<SeriesT>::centerCoefficient(size_type i, size_type r){
  return this->m_coefficientsAtCenter[r].m_x[i];
}

template<class SeriesT>
inline typename PdeCurve<SeriesT>::ScalarType& PdeCurve<SeriesT>::coefficient(size_type i, size_type r) {
  return this->m_coefficients[r].m_x[i];
}

template<class SeriesT>
inline typename PdeCurve<SeriesT>::ScalarType& PdeCurve<SeriesT>::remainderCoefficient(size_type i, size_type r) {
  return this->m_remainderCoefficients[r].m_x[i];
}

template<class SeriesT>
inline typename PdeCurve<SeriesT>::ScalarType& PdeCurve<SeriesT>::coefficient(size_type i, size_type j, size_type r) {
  return this->m_matrixCoefficients[i][r].getCoefficient(++j);
}
*/
template<class SeriesT>
PdeCurve<SeriesT>::PdeCurve(size_type dimension, size_type order)
  : capd::diffAlgebra::ParametricCurve<capd::IMatrix,SeriesT>(1.0,1.0),
    m_order(order)
{
  this->realloc(dimension);
}

template<class SeriesT>
void PdeCurve<SeriesT>::setOrder(size_type order) {
  this->m_order = order;
  this->realloc(this->dimension());
}

template<class SeriesT>
void PdeCurve<SeriesT>::clearCoefficients(){
  for(size_type i=0;i<=this->m_order+1;++i){
    this->m_coefficientsAtCenter[i].clear();
    this->m_coefficients[i].clear();
    this->m_remainderCoefficients[i].clear();
  }
}

template<class SeriesT>
void PdeCurve<SeriesT>::realloc(size_type dim){
  m_coefficientsAtCenter.resize(m_order+2,VectorType(dim));
  m_coefficients.resize(m_order+2,VectorType(dim));
  m_remainderCoefficients.resize(m_order+3,VectorType(dim));
  m_matrixCoefficients.resize(dim,VectorArray(m_order+2,VectorType(dim)));
}

template<class SeriesT>
template<class V>
void PdeCurve<SeriesT>::sumTaylorSeries(V& x, const VectorArray& c, ScalarType h, int p, size_type dim) const{
  for(size_type j=0;j<dim;++j)
    x[j] = c[p][j];
  for(--p;p>=0;--p)
    for(size_type j=0;j<dim;++j)
      x[j] = x[j]*h + c[p][j];
}

template<class SeriesT>
void PdeCurve<SeriesT>::sumTaylorSeries(MatrixType& A, ScalarType h, int p, size_type dim) const{
  for(size_type i=0;i<dim;++i){
    typename MatrixType::RefColumnVectorType r = A.column(i);
    this->sumTaylorSeries(r,this->getMatrixCoefficients()[i],h,p,dim);
  }
}

///@}
}} // namespace capd::diffAlgebra

#endif // _CAPD_PDES_PDECURVE_H_
