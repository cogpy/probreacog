/// @addtogroup pdes
/// @{

/////////////////////////////////////////////////////////////////////////////
/// @file OneDimKSSineVectorField.h
///
/// @author Daniel Wilczak
/////////////////////////////////////////////////////////////////////////////

// Copyright (C) 2008-2016 by the CAPD Group.
//
// Distributed under the terms of the GNU General Public License.
// Consult  http://capd.ii.uj.edu.pl/ for details.

#ifndef _CAPD_PDES_OneDimKSSineVectorField_H_
#define _CAPD_PDES_OneDimKSSineVectorField_H_

#include <vector>
#include <iostream>

#include "capd/auxil/minmax.h"
#include "capd/basicalg/power.h"
#include "capd/intervals/lib.h"
#include "capd/vectalg/lib.h"
#include "capd/pdes/DissipativeVectorField.h"
#include "capd/pdes/GeometricSeries.hpp"

namespace capd {
namespace pdes {
/**
 * The class implements vector field of the one-dimensional real Kuramoto-Shivashinsky PDE under the following assumptions
 * 1 .The solutions are represented in the Fourier basis
 * 2. We impose periodic and odd solutions, thus only sine components are present.
 *    The functions are represented as \f$ u(t,x) = -2 \sum_{k=1}^\infty a_k(t) \sin (ikx) \f$
 * 3. Domain is restricted to some subset of analytic functions. We impose geometric-like decay of Fourier coefficients.
 *    |a_k| < C/(q^k k^s), for some real constants q>1 and s
 *
 * The implementation provides
 * - evaluation of vector field on a representable set of analytic functions
 * - computation of partial derivatives of the vector field with respect to finite number of variables
 * - automatic differentiation for d/dt^i, i-natural number
 * - automatic differentiation for d/da_k dt^i - -natural number k-bounded
*/
class OneDimKSSineVectorField: public DissipativeVectorField<capd::pdes::GeometricSeries>{
public:
  typedef capd::interval ScalarType;
  typedef capd::pdes::GeometricSeries VectorType;
  typedef capd::IMatrix MatrixType;

  typedef capd::IVector::size_type size_type;
  typedef std::vector<VectorType> VectorArray;
  typedef std::vector<VectorArray> MatrixArray;
  typedef std::vector<ScalarType> ScalarArray;

  /// constructs vector field of KS-equation.
  /// @param[in] nu - viscosity parameter in the KS-equation
  OneDimKSSineVectorField(ScalarType nu, size_type dim, size_type firstDissipativeVariable);

  VectorType operator()(ScalarType h, const VectorType& v) {
    VectorArray a(2);
    a[0] = v;
    a[1] = v;
    this->computeODECoefficients(a,1);
    return a[1];
  }

  VectorType operator()(ScalarType h, const VectorType& v, MatrixType& A) {
    VectorArray a(2);
    a[0] = v;
    a[1] = v;
    MatrixArray J(this->dimension(),VectorArray(2,VectorType(this->dimension())));
    for(size_type j=0;j<this->dimension();++j){
      for(size_type c=1;c<=this->dimension();++c)
        J[j][0].setCoefficient(c, j+1==c ? 1. : 0.);
      J[j][0].setGeometricDecay(v.getGeometricDecay());
      J[j][0].setConstant(0.);
    }
    this->computeODECoefficients(a,J,1);
    for(size_type j=0;j<this->dimension();++j){
      for(size_type c=1;c<=this->dimension();++c)
        A(j+1,c) = J[j][1].getCoefficient(c);
    }
    return a[1];
  }

  MatrixType derivative(ScalarType h, const VectorType& v){
    MatrixType A(this->dimension(),this->dimension());
    this->operator()(h,v,A);
    return A;
  }

  void computeODECoefficients(VectorArray& a, size_type order);
  void computeODECoefficients(VectorArray& a, MatrixArray&, size_type order);
  void makeSelfConsistentBound(VectorArray& a);

  size_type dimension() const { return m_dimension; }
  size_type firstDissipativeIndex() const { return m_firstDissipativeVariable; }
  void updateTail(VectorType& x, const VectorArray& a, const VectorArray& enc, ScalarType h, size_type p) const;

private:
  void computeODECoefficients(VectorArray& a, VectorArray&, size_type order);

  ScalarType computeExplicitCoefficient(const VectorArray& a, size_type i, size_type k);
  ScalarType computeExplicitCoefficient(const VectorArray& a, const VectorArray& J, size_type i, size_type k);

  ScalarType computeConstantForInfinitePart(const VectorArray& a, size_type i);
  ScalarType computeConstantForInfinitePart(const VectorArray& a, const VectorArray& J, size_type i);

  ScalarType computeD1(const VectorArray& a, size_type i);
  ScalarType computeD1(const VectorArray& a, const VectorArray& J, size_type i);

  ScalarType computeD2(const VectorArray& a, size_type i);
  ScalarType computeD2(const VectorArray& a, const VectorArray& J, size_type i);

  void computeNextTail(VectorArray& a, size_type i, ScalarType DI);

  // members
  ScalarType nu;
  size_type m_dimension, m_firstDissipativeVariable;
  ScalarArray lambda;
  ScalarArray nonlinearPart;
}; // end of class OneDimKSSineVectorField

// ***************************************************************************

OneDimKSSineVectorField::OneDimKSSineVectorField(ScalarType nu, size_type dim, size_type firstDissipativeVariable)
  : nu(nu), m_dimension(dim), m_firstDissipativeVariable(firstDissipativeVariable),
    lambda(dim+2), nonlinearPart(dim+2)
{
  for(size_type k=1;k<=m_dimension+1;++k){
    size_type k2 = k*k;
    lambda[k] = k2*(1.-nu*k2);
  }
}

// ***************************************************************************

OneDimKSSineVectorField::ScalarType
OneDimKSSineVectorField::computeExplicitCoefficient(const VectorArray& a, size_type i, size_type k) {
  if(k>2*m_dimension)
    throw std::runtime_error("OneDimKSSineVectorField::computeExplicitCoefficient(a,i,k) incorrect index");

  ScalarType s = ScalarType(0.);
  for(size_type j=0;j<=i;++j){
    for(size_type n=1;n<=(k-1)/2;++n)
      s += a[j].getCoefficient(n)*( a[i-j].getCoefficient(n+k) - a[i-j].getCoefficient(k-n) );
    for(size_type n=(k+1)/2;n<=this->m_dimension;++n)
      s += a[j].getCoefficient(n)*a[i-j].getCoefficient(n+k);
  }
  if(k%2==0){
    k /=2;
    size_type j=0;
    for(;j<i/2;++j)
      s -= a[j].getCoefficient(k)*a[i-j].getCoefficient(k);
    if(i%2)
      s -= a[j].getCoefficient(k)*a[j+1].getCoefficient(k);
    else
      s -= 0.5*sqr(a[j].getCoefficient(k));
  }
  return 2.*s;
}

// ***************************************************************************

OneDimKSSineVectorField::ScalarType
OneDimKSSineVectorField::computeExplicitCoefficient(const VectorArray& a, const VectorArray& J, size_type i, size_type k) {
  ScalarType s = ScalarType(0.);
  if(k<=this->m_dimension)
  {
    for(size_type j=0;j<=i;++j){
      for(size_type n=1;n<k;++n)
	s += a[j].getCoefficient(n)*( J[i-j].getCoefficient(n+k) - J[i-j].getCoefficient(k-n) )
	   + J[j].getCoefficient(n)*a[i-j].getCoefficient(n+k);
      for(size_type n=k;n<=this->m_dimension;++n){
	s += a[j].getCoefficient(n)*J[i-j].getCoefficient(n+k);
	s += J[j].getCoefficient(n)*a[i-j].getCoefficient(n+k);
      }
    }
  } else {
      for(size_type j=0;j<=i;++j){
        for(size_type n=1;n<=this->m_dimension;++n)
          s += a[j].getCoefficient(n)*( J[i-j].getCoefficient(n+k) - J[i-j].getCoefficient(k-n) )
  	     + J[j].getCoefficient(n)*( a[i-j].getCoefficient(n+k) - a[i-j].getCoefficient(k-n) );
        for(size_type n=this->m_dimension+1;n<k-this->m_dimension;++n)
          s -= a[j].getCoefficient(n)*J[i-j].getCoefficient(k-n);
      }
  }
  return 2.*s;
}

// ***************************************************************************

OneDimKSSineVectorField::ScalarType
OneDimKSSineVectorField::computeD1(const VectorArray& a, size_type i) {
  ScalarType s = 0.;
  for(size_type j=0;j<=i;++j){
    ScalarType q = 1;
    for(size_type n=1;n<=this->m_dimension;++n){
      q *= a[i-j].getGeometricDecay();
      s += (q+1./q)*a[i-j].getConstant() * abs(a[j].getCoefficient(n));
    }
  }
  s *= 2;
  s /= (2*this->m_dimension+1);

  for(size_type j=0;j<=i;++j)
    s += a[j].getConstant() * a[i-j].getConstant();

  return s.rightBound();
}

// ***************************************************************************

OneDimKSSineVectorField::ScalarType
OneDimKSSineVectorField::computeD1(const VectorArray& a, const VectorArray& J, size_type i) {
  ScalarType s = 0.;
  for(size_type j=0;j<=i;++j){
    ScalarType q = 1;
    for(size_type n=1;n<=this->m_dimension;++n){
      q *= J[i-j].getGeometricDecay();
      s += (q+1./q)*(a[i-j].getConstant() * abs(J[j].getCoefficient(n))+J[i-j].getConstant() * abs(a[j].getCoefficient(n)));
    }
  }
  s /= (2*this->m_dimension+1);

  for(size_type j=0;j<=i;++j)
    s += a[j].getConstant() * J[i-j].getConstant();

  s *= 2.;
  return s.rightBound();
}

// ***************************************************************************

OneDimKSSineVectorField::ScalarType
OneDimKSSineVectorField::computeD2(const VectorArray& a, size_type i) {
  const ScalarType q = a[i].getGeometricDecay();
  ScalarType q1 = power(q,this->m_dimension);
  double d = 0;
  for(size_type k=this->m_dimension+1;k<=2*this->m_dimension;++k){
    q1 *= q;
    double d1 = rightBound( abs(q1*computeExplicitCoefficient(a,i,k)/k) );
    if(d1>d) d = d1;
  }
  return d;
}

// ***************************************************************************

OneDimKSSineVectorField::ScalarType
OneDimKSSineVectorField::computeD2(const VectorArray& a, const VectorArray& J, size_type i) {
  const ScalarType q = a[i].getGeometricDecay();
  ScalarType q1 = power(q,this->m_dimension);
  double d = 0;
  for(size_type k=this->m_dimension+1;k<=2*this->m_dimension;++k){
    q1 *= q;
    double d1 = rightBound( abs(q1*computeExplicitCoefficient(a,J,i,k)/k) );
    if(d1>d) d = d1;
  }
  return d;
}


// ***************************************************************************

OneDimKSSineVectorField::ScalarType
OneDimKSSineVectorField::computeConstantForInfinitePart(const VectorArray& a, size_type i) {
  ScalarType s = 0.;
  for(size_type j=0;j<=i;++j)
    s += a[j].getConstant() * a[i-j].getConstant();

  const ScalarType q = a[i].getGeometricDecay();
  return (s/(power(q,2*this->m_dimension)*(q*q-1.))).rightBound();
}

// ***************************************************************************

OneDimKSSineVectorField::ScalarType
OneDimKSSineVectorField::computeConstantForInfinitePart(const VectorArray& a, const VectorArray& J, size_type i) {
  ScalarType s = 0.;
  for(size_type j=0;j<=i;++j)
    s += a[j].getConstant() * J[i-j].getConstant();

  const ScalarType q = a[i].getGeometricDecay();
  return (2.*s/(power(q,2*this->m_dimension)*(q*q-1.))).rightBound();
}

// ***************************************************************************

void OneDimKSSineVectorField::makeSelfConsistentBound(VectorArray& a) {
  size_type M1 = this->m_dimension+1;
  size_type M2 = M1*M1;
  size_type M3 = M1*M2;
  ScalarType q = a[0].getGeometricDecay();

  bool found;
  for(int maxIt=10000;maxIt>0;maxIt--){
    ScalarType DI = ScalarType(-2,2)*computeConstantForInfinitePart(a,0);
    found = true;
    for(size_type k=this->m_firstDissipativeVariable; k<=this->m_dimension; ++k){
      double left= a[0].getCoefficient(k).leftBound();
      double right=a[0].getCoefficient(k).rightBound();
      nonlinearPart[k] = k*(computeExplicitCoefficient(a,0,k) + DI/power(q,k));
      if(! (right*lambda[k] + nonlinearPart[k] < 0.) ){
        if(right>0)
          right = (-1.01*nonlinearPart[k].rightBound()/lambda[k]).rightBound();
        else
          right = (-0.99*nonlinearPart[k].rightBound()/lambda[k]).rightBound();
        found = false;
      }
      if(! (left*lambda[k] + nonlinearPart[k] > 0.) ){
        if(left<0)
          left =(-1.01*nonlinearPart[k].leftBound()/lambda[k]).leftBound();
        else
          left =(-0.99*nonlinearPart[k].leftBound()/lambda[k]).leftBound();
        found = false;
      }
      if(left>right){
        throw std::runtime_error("OneDimKSSineVectorField::makeSelfConsistentBound - cannot make self-consistent bound. Inequality cannot be solved.");
      }
      a[0].setCoefficient(k,ScalarType(left,right));
    }
    DI = ScalarType(-2,2)*computeConstantForInfinitePart(a,0);
    ScalarType D = ScalarType(-1,1)*max(computeD1(a,0),computeD2(a,0));
    nonlinearPart[M1] = DI/M1 + D;
    ScalarType C = abs(nonlinearPart[M1]/(M2*(nu-ScalarType(1.)/M2))).rightBound();
    if( a[0].getConstant() < C ){
      // otherwise enlarge and check again.
      a[0].setConstant(1.01*C.rightBound());
      found = false;
    }
    if(found) {
      for(size_type i=1;i<this->m_firstDissipativeVariable;++i)
        nonlinearPart[i] = i*(computeExplicitCoefficient(a,0,i) + DI/power(q,i));
      return;
    }
  }

  throw std::runtime_error("OneDimKSSineVectorField::makeSelfConsistentBound - loop limit exceeded.");
}

// ***************************************************************************

void OneDimKSSineVectorField::computeNextTail(VectorArray& a, size_type i, ScalarType DI) {
  // some heuristic to choose delta
  int M1 = this->m_dimension+1;
  ScalarType q = a[i].getGeometricDecay();
  int t = 2;
  ScalarType delta = (t-1+q)/t;
  ScalarType l = log(delta);
  ScalarType L = (this->m_dimension>4/l) ? power(M1,4)/power(delta,M1)
			     : 256./power(l*ScalarType::euler(),4);
  a[i+1].setGeometricDecay((q/delta).leftBound());

  // Fix constant for next level of derivative
  ScalarType D = max(computeD1(a,i),computeD2(a,i));
  int M2 = M1*M1;
  int M3 = M2*M1;
  ScalarType C = (nu-ScalarType(1.)/M2)*a[i].getConstant() + DI/M3 + D/M2;
  a[i+1].setConstant(L*C/(i+1));
}

// ***************************************************************************

void OneDimKSSineVectorField::computeODECoefficients(VectorArray& a, size_type p) {
  for(size_type i=0;i<p;++i){
    ScalarType DI = computeConstantForInfinitePart(a,i);
    ScalarType D = ScalarType(-2.,2.)*DI;
    ScalarType q = a[i].getGeometricDecay();
    for(size_type k=1; k<=this->m_dimension; ++k){
      ScalarType c = lambda[k]*a[i].getCoefficient(k) + k*(computeExplicitCoefficient(a,i,k) + D/q);
      a[i+1].setCoefficient(k,c/(i+1));
      q *= a[i].getGeometricDecay();
    }

    this->computeNextTail(a,i,DI);
  }
}

// ***************************************************************************

void OneDimKSSineVectorField::computeODECoefficients(VectorArray& a, VectorArray& J, size_type p) {
  for(size_type i=0;i<p;++i){
    ScalarType DI = computeConstantForInfinitePart(a,J,i);
    ScalarType D = ScalarType(-2.,2.)*DI;
    ScalarType q = J[i].getGeometricDecay();
    for(size_type k=1; k<=this->m_dimension; ++k){
      ScalarType c = lambda[k]*J[i].getCoefficient(k) + k*(computeExplicitCoefficient(a,J,i,k) + D/q);
      J[i+1].setCoefficient(k,c/(i+1));
      q *= J[i].getGeometricDecay();
    }

    this->computeNextTail(J,i,DI);
  }
}

// ***************************************************************************

void OneDimKSSineVectorField::computeODECoefficients(VectorArray& a, MatrixArray& J, size_type p) {
  this->computeODECoefficients(a,p);
  for(size_type c=0;c<this->m_dimension;++c)
    this->computeODECoefficients(a,J[c],p);
}

// ***************************************************************************

void OneDimKSSineVectorField::updateTail(VectorType& x, const VectorArray& a, const VectorArray& enc, ScalarType h, size_type p) const {
  ScalarType E = enc[0].getConstant();
  ScalarType H = power(ScalarType(0,1)*h,p+1);

  for(size_type k=1;k<=this->m_dimension;++k){
    if(lambda[k]>0) continue;
    ScalarType e = exp(lambda[k]*h);
    ScalarType t = x.getCoefficient(k);
    ScalarType N = -nonlinearPart[k]/lambda[k];
    ScalarType u = (enc[0].getCoefficient(k)-N)*e + N;
    if(! intersection(t,u,t) ){
      throw std::runtime_error("OneDimKSSineVectorField::updateTail - Intersection error\n");
    }
    ScalarType s = a[p].getCoefficient(k);
    for(int i=p-1;i>=0;i--)
      s = s*h + a[i].getCoefficient(k);
    s += enc[p+1].getCoefficient(k)*H;
    intersection(t,s,t);
    x.setCoefficient(k,t);
  }

  // now we update constant for far tail from linear approximation
  size_type M1 = this->m_dimension+1;
  size_type M2 = M1*M1;
  size_type M3 = M2*M1;
  ScalarType u = abs(nonlinearPart[M1]/(M2*(nu-ScalarType(1.)/M2))).rightBound();
  ScalarType K = (E-u)*exp(h*lambda[M1]) + u;
  x.setConstant(K.rightBound());
}


}} // namespace capd::pdes


#endif // _CAPD_PDES_OneDimKSSineVectorField_H_


/// @}
