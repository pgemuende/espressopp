#ifndef _INTEGRATOR_VELOCITY_VERLET_HPP
#define _INTEGRATOR_VELOCITY_VERLET_HPP

#include "MDIntegrator.hpp"

namespace espresso {
  namespace integrator {

    /** Velocity Verlet Integrator */

    class VelocityVerlet : public MDIntegrator {

      public:

        VelocityVerlet(shared_ptr<class espresso::System> system);

        ~VelocityVerlet();

        void setLangevin(shared_ptr<class Langevin> langevin);

        void run(int nsteps);

      private:

        shared_ptr< class Langevin > langevin;

        void integrate1();

        void integrate2();

        void calcForces();

        /** Predicate that returns true if verlet lists must be rebuild. */

        bool rebuild();
    };
  }
}

#endif
