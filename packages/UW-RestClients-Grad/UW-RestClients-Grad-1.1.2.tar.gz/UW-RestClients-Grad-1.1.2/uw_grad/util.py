# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.util.decorators import use_mock
from uw_grad.dao import Grad_DAO


fdao_grad_override = use_mock(Grad_DAO())
