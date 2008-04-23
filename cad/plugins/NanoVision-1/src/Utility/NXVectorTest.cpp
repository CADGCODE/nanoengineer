// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NXVectorTest.h"

CPPUNIT_TEST_SUITE_REGISTRATION(NXVectorTest);
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION(NXVectorTest,
                                      "NXVectorTestSuite");

// ---------------------------------------------------------------------
/* Helper comparison functions  */


template<typename T, int N, template<typename,int> class NXVectorDerived>
void cppunit_assert_vectors_equal(NXVectorBase<T,N,NXVectorDerived> const& pRef,
                                  T answer[N],
                                  T const& delta = 1.0e-8)
{
	for(int n=0; n<N; ++n) {
		CPPUNIT_ASSERT_DOUBLES_EQUAL(double(pRef[n]),
		                             double(answer[n]),
		                             double(delta));
	}
}

template<typename T, int N, template<typename,int> class NXVectorDerived>
void cppunit_assert_points_unequal(NXVectorBase<T,N,NXVectorDerived> const& pRef,
                                   T answer[N],
                                   T const& delta = 1.0e-8)
{
	for(int n=0; n<N; ++n) {
		CPPUNIT_ASSERT(fabs(double(pRef[n])-double(answer[n])) > double(delta));
	}
}

template<typename T, int N,
template<typename,int> class NXVectorDerived,
template<typename,int> class NXVectorDerived2
>
void cppunit_assert_vectors_equal(NXVectorBase<T,N,NXVectorDerived> const& p1Ref,
                                  NXVectorBase<T,N,NXVectorDerived2> const& p2Ref,
                                  T const& delta = 1.0e-8)
{
	for(int n=0; n<N; ++n) {
		CPPUNIT_ASSERT_DOUBLES_EQUAL(double(p1Ref[n]),
		                             double(p2Ref[n]),
		                             double(delta));
	}
}


// ---------------------------------------------------------------------
/* Test-suite */

void NXVectorTest::accessTest(void)
{
	NXVector4d p;
	double answer[4] = { 0.0, 1.0, 2.0, 3.0 };
	p[0] = answer[0]; p[1] = answer[1]; p[2] = answer[2]; p[3] = answer[3];
	double const *const ptr = p.data();
	CPPUNIT_ASSERT(ptr[0] == 0.0);
	CPPUNIT_ASSERT(ptr[1] == 1.0);
	CPPUNIT_ASSERT(ptr[2] == 2.0);
	CPPUNIT_ASSERT(ptr[3] == 3.0);
	cppunit_assert_vectors_equal(p, answer, 0.0);
}

void NXVectorTest::dataTest(void)
{ 
	NXVector4d p;
	NXVectorRef4d pRef;
	pRef = p;
	CPPUNIT_ASSERT(p.data() == pRef.data());
	
    // test copy constructor for deep-copy semantics
	double init[4] = { 2.0, 3.0, -1.0, 6.0 };
	NXVectorRef4d initRef(init);
	NXVector4d initCopy(initRef);
	CPPUNIT_ASSERT(initRef.data() != initCopy.data());
	cppunit_assert_vectors_equal(initRef, initCopy);
    // test copy assignment for deep-copy
	initCopy.zero();
	initCopy = initRef;
	CPPUNIT_ASSERT(initRef.data() != initCopy.data());
	cppunit_assert_vectors_equal(initRef, initCopy);
}

void NXVectorTest::sizeTest(void)
{
	NXVector4d p;
	CPPUNIT_ASSERT(p.size() == 4);
	NXVectorRef3f pRef;
	CPPUNIT_ASSERT(pRef.size() == 3);
}

void NXVectorTest::zeroTest(void)
{
	NXVector4d p;
	p.zero();
	CPPUNIT_ASSERT(p[0] == 0.0);
	CPPUNIT_ASSERT(p[1] == 0.0);
	CPPUNIT_ASSERT(p[2] == 0.0);
	CPPUNIT_ASSERT(p[3] == 0.0);
	
	NXVector<char,2> cp;
	cp.zero();
	CPPUNIT_ASSERT(cp[0] == '\0');
	CPPUNIT_ASSERT(cp[1] == '\0');
}

void NXVectorTest::incrementTest(void)
{
	NXVector4d p;
	double init[4] = { 0.0, 1.0, 2.0, 3.0 };
	p[0] = init[0]; p[1] = init[1]; p[2] = init[2]; p[3] = init[3];
	NXVector4d p2;
	p2.zero();
	p2 += p;
	cppunit_assert_vectors_equal(p2, init);
	double twice[4] = { 0.0, 2.0, 4.0, 6.0 };
	p2 += p2;
	cppunit_assert_vectors_equal(p2, twice, 0.0);
	
}

void NXVectorTest::decrementTest(void)
{
	double zeros[4] = { 0.0, 0.0, 0.0, 0.0 };
	NXVector4d p1;
	p1.zero();
	NXVector4d p2;
	p2.zero();
	p1 -= p2;
	cppunit_assert_vectors_equal(p1, zeros, 0.0);
	
	double init[4] = { 1.0, -2.0, 13.0, -27.0 };
	double answer[4] = { -1.0, 2.0, -13.0, 27.0 };
	NXVectorRef4d initRef(init);
	NXVector4d initCopy = initRef;
	cppunit_assert_vectors_equal(initRef, initCopy);
	initCopy -= initRef;
	cppunit_assert_vectors_equal(initCopy, zeros, 0.0);
	initCopy -= initRef;
	cppunit_assert_vectors_equal(initCopy, answer, 0.0);
}

void NXVectorTest::scalingTest(void)
{
	double init[4] = { 5.0, 8.0, -2.0, 3.0 };
	double const factor = -2.0;
	double answer[4] = { -10.0, -16.0, 4.0, -6.0 };
	NXVectorRef4d p(init);
	p *= factor;
	cppunit_assert_vectors_equal(p, answer, 0.0);
    // check to see if the reference updated the actual array
	for(int n=0; n<4; ++n)
		CPPUNIT_ASSERT(init[n] == answer[n]);
}

void NXVectorTest::invScalingTest(void)
{
	double init[4] = { -10.0, -16.0, 4.0, -6.0 };
	double answer[4] = { 5.0, 8.0, -2.0, 3.0 };
	double const factor = -2.0;
	NXVectorRef4d p(init);
	p /= factor;
	cppunit_assert_vectors_equal(p, answer, 0.0);
    // check to see if the reference updated the actual array
	for(int n=0; n<4; ++n)
		CPPUNIT_ASSERT(init[n] == answer[n]);
}

void NXVectorTest::dotTest(void)
{
	double p1Data[4] = { 5.0, 6.0, 7.0, 8.0 };
	double p2Data[4] = { 8.0, 7.0, 6.0, 5.0 };
	NXVectorRef4d p1(p1Data);
	NXVectorRef4d p2(p2Data);
	double const p1_dot_p2 = dot(p1, p2);
	double const answer = (p1Data[0] * p2Data[0] +
	                       p1Data[1] * p2Data[1] +
	                       p1Data[2] * p2Data[2] +
	                       p1Data[3] * p2Data[3]);
	CPPUNIT_ASSERT(p1_dot_p2 == answer);
}

void NXVectorTest::squared_normTest(void)
{
	double pData[4] = { 5.0, 6.0, 7.0, 8.0 };
	NXVectorRef4d p(pData);
	double const pSquaredNorm = squared_norm(p);
	double const answer = (pData[0] * pData[0] +
	                       pData[1] * pData[1] +
	                       pData[2] * pData[2] +
	                       pData[3] * pData[3]);
	CPPUNIT_ASSERT(pSquaredNorm == answer);
}

void NXVectorTest::normTest(void)
{
	double pData[5] = { 3.0, 4.0, 5.0, 5.0, 5.0 };
	NXVectorRef<double,5> p(pData);
	double const pNorm = norm(p);
	double const answer = 10.0;
	CPPUNIT_ASSERT_DOUBLES_EQUAL(pNorm, answer, 1.0e-8);
}

void NXVectorTest::normalizeSelfTest(void)
{
	double init[4] = { 1.0, 1.0, 1.0, 1.0 };
	NXVector4d initCopy(init);
	initCopy.normalizeSelf();
	double answer[4] = { 0.5, 0.5, 0.5, 0.5 };
	cppunit_assert_vectors_equal(initCopy, answer, 1.0e-8);
	
	NXVector<float,2> pythagoreanPair;
	pythagoreanPair[0] = 3.0f;
	pythagoreanPair[1] = 4.0f;
	pythagoreanPair.normalizeSelf();
	float pythagoreanPairNormalizedValues[2] = { 0.6f, 0.8f };
	NXVectorRef2f pythagoreanPairNormalized(pythagoreanPairNormalizedValues);
	cppunit_assert_vectors_equal(pythagoreanPair,
	                             pythagoreanPairNormalized,
	                             1.0e-8f);
}

void NXVectorTest::normalizedTest(void)
{
	double init[4] = { 1.0, 1.0, 1.0, 1.0 };
	NXVector4d initCopy(init);
	NXVector4d initNormalized = initCopy.normalized();
	double answer[4] = { 0.5, 0.5, 0.5, 0.5 };
	cppunit_assert_vectors_equal(initNormalized, answer, 1.0e-8);
	cppunit_assert_points_unequal(initNormalized, init, 1.0e-8);
}

void NXVectorTest::crossTest(void)
{
	double iData[3] = { 1.0, 0.0, 0.0 };
	double jData[3] = { 0.0, 1.0, 0.0 };
	double kData[3] = { 0.0, 0.0, 1.0 };
	NXVectorRef3d iUnit(iData), jUnit(jData), kUnit(kData);
	NXVector3d iCross = cross(jUnit, kUnit);
	cppunit_assert_vectors_equal(iCross, iUnit);
	NXVector3d jCross = cross(kUnit, iUnit);
	cppunit_assert_vectors_equal(jCross, jUnit);
	NXVector3d kCross = cross(iUnit, jUnit);
	cppunit_assert_vectors_equal(kCross, kUnit);
	
	double pData[3] = {  2.0, 1.0, -1.0 };
	double qData[3] = { -3.0, 4.0,  1.0 };
	double pcrossqData [3] = { 5.0, 1.0, 11.0 };
	NXVectorRef3d p(pData), q(qData);
	NXVector3d r = cross(p,q);
	cppunit_assert_vectors_equal(NXVectorRef3d(pcrossqData), r.data());
	
	int lData[3] = { 0,  1, 1 };
	int mData[3] = { 1, -1, 3 };
	int minus_lcrossm_data[3] = { -4, -1, 1 };
	NXVectorRef<int,3> l(lData), m(mData);
	NXVector<int,3> n = cross(m,l);
	cppunit_assert_vectors_equal(n, minus_lcrossm_data, 0);
}
