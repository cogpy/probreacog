/////////////////////////////////////////////////////////////////////////////
/// @file C0DoubletonSetGeometricTail.h
///
/// @author Daniel Wilczak
/////////////////////////////////////////////////////////////////////////////

// Copyright (C) 2000-2016 by the CAPD Group.
//
// This file constitutes a part of the CAPD library,
// distributed under the terms of the GNU General Public License.
// Consult  http://capd.ii.uj.edu.pl/ for details.

#ifndef _CAPD_PDES_C0DOUBLETONSETGEOMETRICTAIL_H_
#define _CAPD_PDES_C0DOUBLETONSETGEOMETRICTAIL_H_

#include "capd/dynset/C0DoubletonSet.hpp"
#include "capd/dynset/C0TripletonSet.hpp"
#include "capd/pdes/GeometricSeries.hpp"
#include "capd/pdes/PdeSolver.h"

namespace capd{
namespace pdes{

template<typename Policies>
class C0DoubletonSetGeometricTail : public capd::dynset::C0TripletonSet<GeometricSeries::MatrixType,Policies>{
public:
  typedef capd::pdes::GeometricSeries VectorType;
  typedef VectorType::MatrixType MatrixType;
  typedef typename MatrixType::RowVectorType FiniteVectorType;
  typedef typename MatrixType::ScalarType ScalarType;
  typedef typename MatrixType::size_type size_type;
  typedef capd::vectalg::Norm<VectorType,MatrixType> NormType;
  typedef capd::dynset::C0TripletonSet<MatrixType,Policies> BaseSet;
  typedef typename capd::dynset::C0Set<MatrixType>::SetType SetType;
  typedef capd::pdes::PdeSolver<VectorType> DynSysType;
  typedef capd::dynset::DoubletonData<MatrixType> Data;
  typedef Policies Policy;

  C0DoubletonSetGeometricTail(const VectorType& x, ScalarType t = TypeTraits<ScalarType>::zero())
    : BaseSet(FiniteVectorType(x.dimension(),x.getExplicitCoefficients().begin()),t), m_currentSeries(x)
  {}
  C0DoubletonSetGeometricTail(const VectorType& x, const FiniteVectorType& r0, ScalarType t = TypeTraits<ScalarType>::zero())
    : BaseSet(x.projection(r0.dimension()),r0,t), m_currentSeries(x)
  {
    for(size_type i=0;i<r0.dimension();++i)
      m_currentSeries[i] += r0[i];
  }

  C0DoubletonSetGeometricTail(const VectorType& x, const MatrixType& C, const FiniteVectorType& r0, ScalarType t = TypeTraits<ScalarType>::zero())
  : BaseSet(x.projection(r0.dimension()),C,r0,t), m_currentSeries(x)
  {
    m_currentSeries.projection(r0.dimension()) += C*r0;
  }

  C0DoubletonSetGeometricTail(const VectorType& x, const MatrixType& C, const FiniteVectorType& r0, const MatrixType& B, const FiniteVectorType& r, ScalarType t = TypeTraits<ScalarType>::zero())
  : BaseSet(x.projection(r0.dimension()),C,r0,B,r,t), m_currentSeries(x)
  {
    m_currentSeries.projection(r0.dimension()) += C*r0 + B*r;
  }
  /// computes image of the set after one step/iterate of the dynamical system
  void move(DynSysType & dynsys) { move(dynsys,*this); }

  /// computes image of the set after one step/iterate of the dynamical system and stores it in result
  void move(DynSysType & dynsys, C0DoubletonSetGeometricTail& result) const;

  /// This method computes value of functor f at interval vector represented by this set.
  template<class Functional>
  ScalarType evalAt(const Functional& f) const {
    return BaseSet::evalAt(f.getProjection(BaseSet::dimension()));
  }

  VectorType affineTransformation(const MatrixType& A, const VectorType& c) const{
    size_type d = BaseSet::dimension();
    MatrixType M(d,d);
    for(size_type i=1;i<=d;++i)
      for(size_type j=1;j<=d;++j)
    M(i,j) = A(i,j);
    FiniteVectorType u =  BaseSet::affineTransformation(M,FiniteVectorType(d,c.getExplicitCoefficients().begin()));
    VectorType result = m_currentSeries - c;
    for(size_type i=0;i<d;++i)
      result[i] = u[i];
    return result;
  }

  operator VectorType() const { return m_currentSeries; }
  using SetType::operator FiniteVectorType;

  std::string name() const { return "C0DoubletonSetGeometricTail"; }

  const VectorType& getCurrentSeries() const { return m_currentSeries; }
  void setLastEnclosure(const VectorType& enc) { m_enc = enc; }
  const VectorType& getLastEnclosure() const { return m_enc; }

  using BaseSet::get_x;
  using BaseSet::getElement_x;
  using BaseSet::affineTransformation;
//protected:
  using BaseSet::m_x;
  using BaseSet::m_r;
  VectorType m_currentSeries, m_enc;

};

// -----------------------------------------------------------------------------------

template<typename Policies>
void C0DoubletonSetGeometricTail<Policies>::move(DynSysType & dynsys, C0DoubletonSetGeometricTail& result) const
{
  // the following function can throw an exception leaving output parameters in an inconsistent state
  // do not overwrite parameters of the set until we are sure that they are computed correctly
  if(subset(this->m_x,this->m_currentSet)){
      result.x = this->m_x;
      result.deltaX = this->m_currentSet-this->m_x;
  }else
    split(this->m_currentSet, result.x, result.deltaX);
  if(&result!=this)
    result.m_currentSeries = this->m_currentSeries;
  dynsys.encloseC0Map(result.x,result.m_currentSeries,result.y, result.rem, result.m_enc, result.jacPhi);

  BaseSet::move(*this,result,result.m_currentSet,result);
  result.setCurrentTime(this->getCurrentTime()+dynsys.getStep());
  this->Policies::reorganizeIfNeeded(result);
  for(size_type i=0;i<result.m_currentSet.dimension();++i){
    ScalarType t = result.m_currentSeries[i];
    intersection(t,result.m_currentSet[i],result.m_currentSet[i]);
    result.m_currentSeries[i]=result.m_currentSet[i];
  }
}

/// @}

}} // namespace capd::dynset

#endif // _CAPD_PDES_C0DOUBLETONSETGEOMETRICTAIL_H_
