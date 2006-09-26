/*
  Name: cppsurface.h
  Copyright: 2006 Nanorex, Inc.  All rights reserved.
  Author: Oleksandr Shevchenko
  Description: CPP functions to call from C 
*/

#if !defined(CPPSURFACE_INCLUDED)
#define CPPSURFACE_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

void cppAdd(double x, double y, double z, double r, int p);
void cppCreateSurface();
void cppAllocate();
void cppFree();
int cppNp();
int cppNt();
int cppNc();
double cppPx(int i);
double cppPy(int i);
double cppPz(int i);
double cppNx(int i);
double cppNy(int i);
double cppNz(int i);
double cppCr(int i);
double cppCg(int i);
double cppCb(int i);
int cppI(int i);
void cppLevel(int i);
int cppType();
void cppMethod(int i);

#ifdef __cplusplus
}
#endif

#endif  								// CPPSURFACE_INCLUDED
