/*
calcsnipprio.cpp : This file is part bob-rheology (bob) 
bob-2.5 : rheology of Branch-On-Branch polymers
Copyright (C) 2006-2011, 2012 C. Das, D.J. Read, T.C.B. McLeish
 
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details. You can find a copy
  of the license at <http://www.gnu.org/licenses/gpl.txt>
*/

#include "../../../include/bob.h"
#include <stdio.h>
#include <cstdlib>
#include <vector>
std::vector<std::vector<double> > vector_savedprio;
void calcsnipprio(void)
{
  extern void calc_snip_priority(int);
  extern std::vector<arm> arm_pool;
  extern std::vector<polymer> branched_poly;
  extern std::vector<polycopy> br_copy;
  extern int num_poly;
  // FILE *fpr = fopen("savedprio.dat", "w");
  int n = vector_savedprio.size();
  for (int i = 0; i < n; i++)
    vector_savedprio[i].clear();
  vector_savedprio.clear();
  std::vector<double> temp;
  temp.resize(1);
  for (int i = 0; i < num_poly; i++)
  {
    if (branched_poly[i].alive)
    {
      calc_snip_priority(i);
      int orig_narm = br_copy[i].narm;
      int n1 = branched_poly[i].first_end;
      for (int k = 0; k < orig_narm; k++)
      {
        if (br_copy[i].armindx[k] == n1)
        {
          br_copy[i].priority[k] = arm_pool[n1].priority;
        }
      }
      int n2 = arm_pool[n1].down;
      while (n2 != n1)
      {
        for (int k = 0; k < orig_narm; k++)
        {
          if (br_copy[i].armindx[k] == n2)
          {
            br_copy[i].priority[k] = arm_pool[n2].priority;
          }
        }
        n2 = arm_pool[n2].down;
      }
    }

    for (int k = 0; k < br_copy[i].narm; k++)
    {
      // fprintf(fpr, " %d \n", br_copy[i].priority[k]);
      temp[0] = br_copy[i].priority[k];
      vector_savedprio.push_back(temp);
    }
  }
  // fclose(fpr);
}

void dumpsnipprio(void)
{
  extern std::vector<polycopy> br_copy;
  extern int num_poly;
  int counter = 0;
  // extern double cur_time;
  // FILE *fpr = fopen("savedprio.dat", "r");
  // if (fpr == NULL)
  // {
  //   my_abort((char *)"Was expecting file savedprio.dat here \ndeformation rate too low?? aborting... \n");
  // }

  for (int i = 0; i < num_poly; i++)
  {
    for (int k = 0; k < br_copy[i].narm; k++)
    {
      // fscanf(fpr, " %d ", &br_copy[i].priority[k]);
      br_copy[i].priority[k] = int(vector_savedprio[counter][0]);
      counter++;
    }
  }
  // fclose(fpr);
  // fpr = fopen("savedprio.dat", "w");
  int n = vector_savedprio.size();
  for (int i = 0; i < n; i++)
    vector_savedprio[i].clear();
  vector_savedprio.clear();
  std::vector<double> temp;
  temp.resize(4);
  for (int i = 0; i < num_poly; i++)
  {
    for (int k = 0; k < br_copy[i].narm; k++)
    {
      // fprintf(fpr, " %d %e %e %e \n", br_copy[i].priority[k], br_copy[i].trelax[k],
              // br_copy[i].taus[k], br_copy[i].zeta[k]);
      temp[0] = br_copy[i].priority[k];
      temp[1] = br_copy[i].trelax[k];
      temp[2] = br_copy[i].taus[k];
      temp[3] = br_copy[i].zeta[k];
      vector_savedprio.push_back(temp);
    }
  }
  // fclose(fpr);
}
