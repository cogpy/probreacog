/// @addtogroup pdes
/// @{

/////////////////////////////////////////////////////////////////////////////
/// @file GeometricSeries.hpp
///
/// @author Daniel Wilczak
/////////////////////////////////////////////////////////////////////////////

// Copyright (C) 2008-2016 by the CAPD Group.
//
// Distributed under the terms of the GNU General Public License.
// Consult  http://capd.ii.uj.edu.pl/ for details.


#ifndef _CAPD_PDES_GeometricSeries_HPP_
#define _CAPD_PDES_GeometricSeries_HPP_

#include "capd/pdes/GeometricSeries.h"
namespace capd {
namespace pdes {

// ---------------------------- constructors ----------------------------------

GeometricSeries::GeometricSeries(size_type dim)
  : m_x(dim), m_C(0.), m_q(2.)
{
  this->check();
}

GeometricSeries::GeometricSeries(size_type dim, ScalarType C, ScalarType q)
  : m_x(dim), m_C(C.rightBound()), m_q(q.rightBound())
{
  this->check();
}

GeometricSeries::GeometricSeries(size_type dim, ScalarType C, ScalarType q, const ScalarType* coeff)
  : m_x(dim,coeff), m_C(C.rightBound()), m_q(q.rightBound())
{
  this->check();
}

GeometricSeries::GeometricSeries(ScalarType C, ScalarType q, const FiniteVectorType& u)
  : m_x(u), m_C(C.rightBound()), m_q(q.rightBound())
{
  this->check();
}

void GeometricSeries::check(){
  if(m_q<=1.)
  {
    throw std::runtime_error("GeometricSeries::check - object in an inconsistent state (q<=1)");
  }
}

// --------------------------- operator+ --------------------------------------

GeometricSeries operator+(const GeometricSeries& x, const GeometricSeries& y) {
  return GeometricSeries(
      x.getConstant()+y.getConstant(),
      capd::min(x.getGeometricDecay(),y.getGeometricDecay()),
      x.getExplicitCoefficients() + y.getExplicitCoefficients()
  );
}

GeometricSeries& GeometricSeries::operator+=(const GeometricSeries& y) {
  this->m_C += y.getConstant();
  this->m_q = capd::min(this->getGeometricDecay(),y.getGeometricDecay());
  this->m_x += y.getExplicitCoefficients();
  return *this;
}

// --------------------------- operator- --------------------------------------
GeometricSeries operator-(const GeometricSeries& x, const GeometricSeries& y) {
  return GeometricSeries(
      x.getConstant()+y.getConstant(),
      capd::min(x.getGeometricDecay(),y.getGeometricDecay()),
      x.getExplicitCoefficients() - y.getExplicitCoefficients()
  );
}

GeometricSeries& GeometricSeries::operator-=(const GeometricSeries& y) {
  this->m_C += y.getConstant();
  this->m_q = capd::min(this->getGeometricDecay(),y.getGeometricDecay());
  this->m_x -= y.getExplicitCoefficients();
  return *this;
}

// ----------------------------------------------------------------------------

GeometricSeries operator*(const interval& s, const GeometricSeries& x) {
  return GeometricSeries(
      x.getConstant()*s,
      x.getGeometricDecay(),
      s*x.getExplicitCoefficients()
  );
}

GeometricSeries operator*(const GeometricSeries& x, const interval& s) {
  return s*x;
}

GeometricSeries& GeometricSeries::operator*=(const ScalarType& s) {
  this->m_C *= s;
  this->m_x *= s;
  return *this;
}

// ----------------------------------------------------------------------------
/**
 * This operator realizes the following Matrix by vector multiplication
 * (A*mainVariables,Id*tail)
 */
GeometricSeries operator*(const IMatrix& A, const GeometricSeries& v) {
  if (A.numberOfRows() > v.dimension() || A.numberOfColumns() > v.dimension())
    throw std::runtime_error("Cannot multiply matrix by GeometricSeries - incorrect dimensions");

  GeometricSeries::FiniteVectorType x = A*GeometricSeries::FiniteVectorType(A.numberOfColumns(),v.getExplicitCoefficients().begin());
  GeometricSeries result = v;
  result.projection(A.numberOfRows()) = A*v.projection(A.numberOfColumns());
  return result;
}

// ----------------------------------------------------------------------------

std::ostream& operator << (std::ostream& out, const GeometricSeries& x)
{
  out << "{"
      << x.getExplicitCoefficients() << ","
      << x.getConstant() << ","
      << x.getGeometricDecay() << "}";
  return out;
}

// ----------------------------------------------------------------------------

void split(const GeometricSeries& X, GeometricSeries& x, GeometricSeries& dx){
  x.setConstant(0.);
  x.setGeometricDecay(X.getGeometricDecay());
  dx.setConstant(X.getConstant());
  dx.setGeometricDecay(X.getGeometricDecay());
  split(X.getExplicitCoefficients(),x.getExplicitCoefficients(),dx.getExplicitCoefficients());
}

// ----------------------------------------------------------------------------

GeometricSeries intersection(const GeometricSeries& x, const GeometricSeries& y){
  double qX = x.getGeometricDecay().rightBound();
  double qY = y.getGeometricDecay().rightBound();
  double cX = x.getConstant().rightBound();
  double cY = y.getConstant().rightBound();

  if(qX==qY)
    return GeometricSeries(
        capd::min(cX,cY),
        qX,
        intersection(x.getExplicitCoefficients(),y.getExplicitCoefficients())
    );
  if(qX>qY)
      return GeometricSeries(
          cX,
          qX,
          intersection(x.getExplicitCoefficients(),y.getExplicitCoefficients())
      );
  return GeometricSeries(
      cY,
      qY,
      intersection(x.getExplicitCoefficients(),y.getExplicitCoefficients())
  );
}

} // end of namespace pdes
} // end of namespace capd

#endif // _CAPD_PDES_GeometricSeries_HPP_

/// @}


