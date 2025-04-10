# Copyright 2025 The Newton Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Tests for constraint functions."""

import mujoco
import numpy as np
from absl.testing import absltest
from absl.testing import parameterized

import mujoco_warp as mjwarp

from .types import ConeType
from . import test_util

# tolerance for difference between MuJoCo and MJWarp constraint calculations,
# mostly due to float precision
_TOLERANCE = 5e-5


def _assert_eq(a, b, name):
  tol = _TOLERANCE * 10  # avoid test noise
  err_msg = f"mismatch: {name}"
  np.testing.assert_allclose(a, b, err_msg=err_msg, atol=tol, rtol=tol)


class ConstraintTest(parameterized.TestCase):
  @parameterized.parameters(
    (ConeType.PYRAMIDAL, 1, 1),
    (ConeType.PYRAMIDAL, 1, 3),
    (ConeType.PYRAMIDAL, 1, 4),
    (ConeType.PYRAMIDAL, 1, 6),
    (ConeType.PYRAMIDAL, 3, 3),
    (ConeType.PYRAMIDAL, 3, 4),
    (ConeType.PYRAMIDAL, 3, 6),
    (ConeType.PYRAMIDAL, 4, 4),
    (ConeType.PYRAMIDAL, 4, 6),
    (ConeType.PYRAMIDAL, 6, 6),
    (ConeType.ELLIPTIC, 1, 1),
    (ConeType.ELLIPTIC, 1, 3),
    (ConeType.ELLIPTIC, 1, 4),
    (ConeType.ELLIPTIC, 1, 6),
    (ConeType.ELLIPTIC, 3, 3),
    (ConeType.ELLIPTIC, 3, 4),
    (ConeType.ELLIPTIC, 3, 6),
    (ConeType.ELLIPTIC, 4, 4),
    (ConeType.ELLIPTIC, 4, 6),
    (ConeType.ELLIPTIC, 6, 6),
  )
  def test_condim(self, cone, condim1, condim2):
    """Test condim."""
    xml = f"""
      <mujoco>
        <worldbody>
          <body pos="0.0 0 0">
            <freejoint/>
            <geom type="sphere" size=".1" condim="{condim1}"/>
          </body>
          <body pos="0.05 0 0">
            <freejoint/>
            <geom type="sphere" size=".1" condim="{condim2}"/>
          </body>
        </worldbody>
      </mujoco>
    """

    _, mjd, m, d = test_util.fixture(xml=xml, cone=cone)
    mjwarp.make_constraint(m, d)

    _assert_eq(d.efc.J.numpy()[: mjd.nefc, :].reshape(-1), mjd.efc_J, "efc_J")
    _assert_eq(d.efc.D.numpy()[: mjd.nefc], mjd.efc_D, "efc_D")
    _assert_eq(d.efc.aref.numpy()[: mjd.nefc], mjd.efc_aref, "efc_aref")
    _assert_eq(d.efc.pos.numpy()[: mjd.nefc], mjd.efc_pos, "efc_pos")
    _assert_eq(d.efc.margin.numpy()[: mjd.nefc], mjd.efc_margin, "efc_margin")

  @parameterized.parameters(
    mujoco.mjtCone.mjCONE_PYRAMIDAL,
    mujoco.mjtCone.mjCONE_ELLIPTIC,
  )
  def test_constraints(self, cone):
    """Test constraints."""
    mjm, mjd, _, _ = test_util.fixture("constraints.xml", cone=cone)

    for key in range(3):
      mujoco.mj_resetDataKeyframe(mjm, mjd, key)

      mujoco.mj_forward(mjm, mjd)
      m = mjwarp.put_model(mjm)
      d = mjwarp.put_data(mjm, mjd)
      mjwarp.make_constraint(m, d)

      _assert_eq(d.efc.J.numpy()[: mjd.nefc, :].reshape(-1), mjd.efc_J, "efc_J")
      _assert_eq(d.efc.D.numpy()[: mjd.nefc], mjd.efc_D, "efc_D")
      _assert_eq(d.efc.aref.numpy()[: mjd.nefc], mjd.efc_aref, "efc_aref")
      _assert_eq(d.efc.pos.numpy()[: mjd.nefc], mjd.efc_pos, "efc_pos")
      _assert_eq(d.efc.margin.numpy()[: mjd.nefc], mjd.efc_margin, "efc_margin")
      _assert_eq(d.ne.numpy()[0], mjd.ne, "ne")


if __name__ == "__main__":
  absltest.main()
