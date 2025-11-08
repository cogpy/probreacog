/// @addtogroup diffIncl
/// @{

/////////////////////////////////////////////////////////////////////////////
/// @file InclRect2Set.hpp
///
/// @author The CAPD Group
/////////////////////////////////////////////////////////////////////////////

// Copyright (C) 2000-2014 by the CAPD Group.
//
// This file constitutes a part of the CAPD library, 
// distributed under the terms of the GNU General Public License.
// Consult  http://capd.ii.uj.edu.pl/ for details.

#ifndef _CAPD_DIFFINCL_INCLRECT2SET_HPP_ 
#define _CAPD_DIFFINCL_INCLRECT2SET_HPP_ 

#include "capd/diffIncl/InclRect2Set.h"
#include "capd/dynset/C0DoubletonSet.hpp"
#include "capd/vectalg/Norm.hpp"
#include <iostream>

namespace capd{
  namespace diffIncl{
    
    
    template<typename MatrixType>
    template<typename DiffIncl>
    void InclRect2Set<MatrixType>::move(DiffIncl & diffIncl) {
      
      VectorType x = VectorType(*this);
      
      //VectorType x = m_x + m_C * m_r0 + m_B * m_r; //VectorType(*this);
      //this->m_currentSet = x;
      ScalarType currentTime = this->getCurrentTime();
      //computation of an unperturbed trajectory
      BaseSet::move(diffIncl.getDynamicalSystem());
      
      //computation of the influence of the perturbations
      VectorType Deltha = diffIncl.perturbations(currentTime, x);
      
      // Rearrangements
      x = midVector( m_x + Deltha);
      VectorType dr = m_x - x + Deltha;
     
      m_r = m_r + this->get_invB() * dr;
      m_x = x;

      //this->m_currentSet += m_x + m_C * m_r0 + m_B * m_r;
      this->m_currentSet += Deltha;
    }
    
    template<typename MatrixType>
    template<typename DiffIncl>
    void InclRect2Set<MatrixType>::move(DiffIncl & diffIncl, InclRect2Set<MatrixType>& result) const {
      VectorType x = VectorType(*this);
      ScalarType currentTime = this->getCurrentTime();
       
      //computation of an unperturbed trajectory
      BaseSet::move(diffIncl.getDynamicalSystem(), result);
      
      //computation of the influence of the perturbations
      VectorType Deltha = diffIncl.perturbations(currentTime, x);
      
      // Rearrangements
      x = capd::vectalg::midVector( result.m_x + Deltha);
      VectorType dr = result.m_x + Deltha - x;
      
      result.m_r = result.m_r + result.get_invB() * dr;
      result.m_x = x;

//      result.m_currentSet = result.m_x + result.m_C * result.m_r0 + result.m_B * result.m_r;
      result.m_currentSet += Deltha;
    }
    
    template<typename T>
    void corners(T& head, const T & tail, int i, int dim, std::vector<T> & cor) {
      if(i < dim) {
        head[i] = left(tail[i]);
        corners(head, tail, i+1, dim, cor);
        head[i] = right(tail[i]);
        corners(head, tail, i+1, dim, cor);
        head[i] = tail[i];
      }
      else {
        cor.push_back(head);
      }
    }
    
    
    template<typename SetType>
    std::vector<typename SetType::VectorType> getCorners(const SetType & set) {
      typedef typename SetType::VectorType VectorType;
      std::vector<VectorType> cor;
      VectorType v = set.get_r();
      corners(v, set.get_r(), 0, v.dimension(), cor);
      for(typename std::vector<VectorType>::iterator it = cor.begin(); it != cor.end(); ++it){
        *it = set.get_x() + set.get_C() * set.get_r0() + set.get_B() * *it;
      }
      return cor;
    }
    
    template<typename MatrixType>
    std::vector<typename InclRect2Set<MatrixType>::VectorType> InclRect2Set<MatrixType>::getCorners() const {
      return ::capd::diffIncl::getCorners(*this);
    }
    
  }} // namespace capd::diffIncl

#endif // _CAPD_DIFFINCL_INCLRECT2SET_HPP_ 

/// @}
