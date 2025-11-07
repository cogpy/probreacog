/// @addtogroup pdes
/// @{

/////////////////////////////////////////////////////////////////////////////
/// @file PdeSolver.h
///
/// @author Daniel Wilczak
/////////////////////////////////////////////////////////////////////////////

// Copyright (C) 2008-2016 by the CAPD Group.
//
// Distributed under the terms of the GNU General Public License.
// Consult  http://capd.ii.uj.edu.pl/ for details.

#ifndef _CAPD_PDES_PDESOLVER_H_
#define _CAPD_PDES_PDESOLVER_H_

#include <vector>
#include <iostream>

#include "capd/auxil/minmax.h"
#include "capd/basicalg/power.h"
#include "capd/intervals/lib.h"
#include "capd/vectalg/lib.h"
#include "capd/dynsys/approveRemainder.h"
#include "capd/pdes/PdeCurve.h"
#include "capd/pdes/DissipativeVectorField.h"

namespace capd {
namespace pdes {

//template<class SeriesT, class StepControlT = capd::dynsys::FixedStepControl<capd::interval> >
template<class SeriesT, class StepControlT = capd::dynsys::ILastTermsStepControl>
class PdeSolver : public PdeCurve<SeriesT>, public capd::dynsys::StepControlInterface<StepControlT,typename SeriesT::ScalarType> {
public:
  typedef SeriesT VectorType;
  typedef StepControlT StepControlType;

  typedef capd::IVector FiniteVectorType;
  typedef PdeCurve<VectorType> CurveType;
  typedef PdeCurve<VectorType> SolutionCurve;
  typedef capd::IMatrix MatrixType;
  typedef typename MatrixType::ScalarType ScalarType;
  typedef typename TypeTraits<ScalarType>::Real Real;
  typedef typename MatrixType::size_type size_type;
  typedef DissipativeVectorField<VectorType> MapType;
  typedef typename CurveType::VectorArray VectorArray;
  typedef typename CurveType::MatrixArray MatrixArray;

  PdeSolver(MapType& f, size_type order);
  ~PdeSolver(){}

  const CurveType& getCurve()  const {
    this->setDomain(0.,rightBound(this->m_step));
    return *this;
  }
  CurveType& getCurve() {
    this->setDomain(0.,rightBound(this->m_step));
    return *this;
  }
  const CurveType& getImplicitCurve() const { return this->m_implicitCurve; }

  template <typename SetType>
  void operator()(SetType& set){
    set.move(*this);
  }

  /// Computes image of the set (in set's representation) and stores it in the result set.
   /// @param[in]  set       C^0 or C^1  set representing initial conditions
   /// @param[out] result    on return contains image of the set
  template <typename SetType>
  void operator()(SetType& set, SetType& result){
    set.move(*this,result);
  }

  MapType& getVectorField() { return *m_vectorField; }

  void encloseC0Map(
      const FiniteVectorType& x0, //< @param[in] an internal point of x, usually center of x
      VectorType& x,      	      //< @param[in] set to be moved along by the flow
      FiniteVectorType& o_phi,    //< @param[out] bound for phi(x0), where phi is a numerical method
      FiniteVectorType& o_rem,    //< @param[out] bound for the error of numerical method over the time step
      VectorType& o_enc,    	    //< @param[out] enclosure of all trajectories starting from x over the time interval (time step of numerical method)
      MatrixType& o_jacPhi  	    //< @param[out] bound for derivative Dphi(x) on finite number of modes
  );

  void computeImplicitCoefficients(
    const FiniteVectorType& x0,     //< @param[in] an internal point of x, usually center of x
    const VectorType& x,        	  //< @param[in] set to be moved along the trajectories of ODE
    size_type q
  );

  void initRemainderCoefficients(ScalarType t, const VectorType& x, unsigned /*degree*/){
    this->m_vectorField->computeODECoefficients(this->getRemainderCoefficients(),this->getOrder()+1);
  }

  void computeTimeStep(const ScalarType& t, const VectorType& x){
    this->m_step = this->isStepChangeAllowed()
        ? this->getStepControl().computeNextTimeStep(*this,t,x.getExplicitCoefficients())
        : capd::min(this->m_fixedTimeStep,this->getMaxStep());
  }

  void setStep(ScalarType h) {
      m_fixedTimeStep = h;
      this->turnOffStepControl();
  }
  void adjustTimeStep(ScalarType h) { this->m_step = h; }
  ScalarType getStep() { return m_step; }

  ScalarType getCoeffNorm(size_type, size_type degree) const;
protected:

  void setInitialCondition(const FiniteVectorType& x0, const VectorType& x, CurveType& curve);
  void highOrderEnclosure();
  void enclosure(FiniteVectorType& o_enc, FiniteVectorType& o_rem);
  CurveType m_implicitCurve;
  MapType* m_vectorField;
  ScalarType m_step;
  ScalarType m_fixedTimeStep;
  MatrixType m_jacPhi;
  FiniteVectorType m_phi, m_deltaX, m_rem;
}; // end of class PdeSolver

// ***************************************************************************
template<class SeriesT,class StepControlT>
inline PdeSolver<SeriesT,StepControlT>::PdeSolver(MapType& vf, size_type order)
  : CurveType(vf.dimension(), order),
    m_vectorField(&vf),
    m_implicitCurve(vf.dimension(),order),
    m_jacPhi(vf.dimension(),vf.dimension()),
    m_phi(vf.dimension()),
    m_deltaX(vf.dimension()),
    m_rem(vf.dimension())
{
  if (order<1)
    throw std::runtime_error("PdeSolver constructor - order of the method cannot be less than 1.");
}

// ***************************************************************************

template<class SeriesT,class StepControlT>
void PdeSolver<SeriesT,StepControlT>::setInitialCondition(
      const FiniteVectorType& x0, const VectorType& x, CurveType& curve
    )
{
  size_type i,j,c;
  size_type m = x0.dimension();
  size_type M = this->m_vectorField->dimension();
  ScalarType q = x.getGeometricDecay();

  VectorArray& center = curve.getCoefficientsAtCenter();
  VectorArray& X = curve.getCoefficients();
  MatrixArray& J = curve.getMatrixCoefficients();

  center[0] = x;
  for(i=0;i<m;++i){
    center[0][i] = x0[i];
    m_deltaX[i] = x[i]-x0[i];
  }
  for(;i<M;++i)
    center[0][i].split(m_deltaX[i]);

  // set initial condition
  X[0] = x;
  // set Identity as an initial condition for variational equations
  for(size_type j=0;j<M;++j){
    for(size_type c=1;c<=M;++c)
      J[j][0].setCoefficient(c, j+1==c ? 1. : 0.);
    J[j][0].setGeometricDecay(q);
    J[j][0].setConstant(0.);
  }
}
  // ***************************************************************************

template<class SeriesT,class StepControlT>
void PdeSolver<SeriesT,StepControlT>::encloseC0Map(
    const FiniteVectorType& x0, VectorType& x,
    FiniteVectorType& o_phi, FiniteVectorType& o_rem, VectorType& o_enc,
    MatrixType& o_jacPhi
){
  size_type p = this->getOrder();
  size_type m = x0.dimension();
  size_type M = this->m_vectorField->dimension();
  size_type i,j,c;
  ScalarType q = x.getGeometricDecay();

  VectorArray& center = this->getCoefficientsAtCenter();
  VectorArray& X = this->getCoefficients();
  MatrixArray& J = this->getMatrixCoefficients();
  VectorArray& enc = this->getRemainderCoefficients();

  this->setInitialCondition(x0,x,*this);

  this->m_vectorField->computeODECoefficients(center,p);
  this->m_vectorField->computeODECoefficients(X,J,p);

  this->computeTimeStep(0.,x);
  this->highOrderEnclosure();

  this->sumTaylorSeries(m_phi,center,m_step,p,M);
  this->sumTaylorSeries(m_jacPhi,m_step,p,M);
  x.setExplicitCoefficients(m_phi + m_jacPhi*m_deltaX + m_rem);
  for(i=0;i<m;++i){
    o_rem[i] = m_rem[i];
    o_phi[i] = m_phi[i];
    for(j=m;j<M;++j)
      o_phi[i] += m_jacPhi(i+1,j+1)*m_deltaX[j];
    for(j=0;j<m;++j)
      o_jacPhi(i+1,j+1) = m_jacPhi(i+1,j+1);
  }
  this->m_vectorField->updateTail(x,X,enc,m_step,p);
  o_enc = enc[0];
}

// ***************************************************************************

template<class SeriesT,class StepControlT>
void PdeSolver<SeriesT,StepControlT>::computeImplicitCoefficients(
    const FiniteVectorType& x0, const VectorType& x, size_type p
){
  VectorArray& center = this->m_implicitCurve.getCoefficientsAtCenter();
  VectorArray& X = this->m_implicitCurve.getCoefficients();
  MatrixArray& J = this->m_implicitCurve.getMatrixCoefficients();

  this->setInitialCondition(x0,x,this->m_implicitCurve);
  this->m_vectorField->computeODECoefficients(center,p);
  this->m_vectorField->computeODECoefficients(X,J,p);
}

// ***************************************************************************

template<class SeriesT,class StepControlT>
typename PdeSolver<SeriesT,StepControlT>::ScalarType
PdeSolver<SeriesT,StepControlT>::getCoeffNorm(size_type r, size_type /*degree*/) const
{
  typename TypeTraits<ScalarType>::Real result = 0;
  for(size_type i=0;i<this->dimension();++i){
    result = capd::max(result,rightBound(abs(this->remainderCoefficient(i,r))));
    result = capd::max(result,rightBound(abs(this->coefficient(i,r))));
  }
  return ScalarType(result);
}

// ***************************************************************************

template<class SeriesT,class StepControlT>
void PdeSolver<SeriesT,StepControlT>::highOrderEnclosure()
{
  size_type d = this->m_vectorField->firstDissipativeIndex()-1;
  size_type M = this->m_vectorField->dimension();
  size_type p = this->getOrder();
  VectorArray& X = this->getCoefficients();
  VectorArray& enc = this->getRemainderCoefficients();
  FiniteVectorType rem(M);
  FiniteVectorType E(d);

  double tol = this->getAbsoluteTolerance();
  ScalarType R = tol*ScalarType(-1.,1.);
  m_step = capd::min(this->m_step,this->getMaxStep());
  ScalarType I = ScalarType(0,1)*m_step;
  ScalarType IP = power(I,p+1);

  int counter = d*5;
  while(counter){
    enc[0] = X[0];
    this->sumTaylorSeries(enc[0].getExplicitCoefficients(),X,I,p,d);
    for(size_type n=0;n<d;++n){
      if(enc[p+1][n]==0.){
        rem[n] = R;
      } else
        rem[n] = ScalarType(-2,2)*IP*enc[p+1][n];
      enc[0][n] += rem[n];
    }
    this->m_vectorField->makeSelfConsistentBound(enc);
    this->m_vectorField->computeODECoefficients(enc,p+1);
    // check inclusion
    ScalarType beta = 1;
    bool success = true;
    m_rem = enc[p+1].getExplicitCoefficients()*IP;
    for(size_type n=0;n<d;++n){
      if(subsetInterior(m_rem[n],rem[n])) continue;
      success = false;
      ScalarType c = rem[n].rightBound()/abs(m_rem[n]).right();
      c = exp(log(c)/(p+1));
      beta = capd::min(beta,c);
    }
    if(success) return;
    if(this->isStepChangeAllowed()){
      m_step = (m_step*beta).leftBound();
      m_rem *= power(beta,p+1);
      return;
    }
    counter--;
  }
  throw capd::dynsys::SolverException<VectorType>("PdeSolver::highOrderEnclosure - cannot find an enclosure",0.,X[0],m_step);
}
}} // namespace capd::pdes


#endif // _CAPD_PDES_PDESOLVER_H_


/// @}
