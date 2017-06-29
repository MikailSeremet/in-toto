"""
<Program Name>
  test_in_toto_keygen.py
<Author>
  Sachit Malik <i.sachitmalik@gmail.com>
<Started>
  Wed Jun 28, 2017
<Copyright>
  See LICENSE for licensing information.
<Purpose>
  Test in_toto_keygen command line tool.
"""

import os
import sys
import unittest
import logging
import argparse
import shutil
import tempfile
from mock import patch
from in_toto.in_toto_keygen import main as in_toto_keygen_main
from in_toto.in_toto_keygen import (generate_and_write_rsa_keypair, \
    prompt_generate_and_write_rsa_keypair, prompt_password)
from in_toto.util import (import_rsa_key_from_file,
    import_rsa_public_keys_from_files_as_dict, prompt_import_rsa_key_from_file)
from in_toto import log
from in_toto import exceptions
import securesystemslib
from securesystemslib.keys import generate_rsa_key

WORKING_DIR = os.getcwd()

# Suppress all the user feedback that we print using a base logger
logging.getLogger().setLevel(logging.CRITICAL)

class TestInTotoKeyGenTool(unittest.TestCase):
  """Test in_toto_keygen's main() - requires sys.argv patching; error
  logs/exits on Exception. """

  @classmethod
  def setUpClass(self):
    # Create directory where the verification will take place
    self.working_dir = os.getcwd()
    self.test_dir = os.path.realpath(tempfile.mkdtemp())
    os.chdir(self.test_dir)

  @classmethod
  def tearDownClass(self):
    """Change back to initial working dir and remove temp test directory. """
    os.chdir(self.working_dir)
    shutil.rmtree(self.test_dir)

  def test_main_required_args(self):
    """Test in-toto-keygen CLI tool with required arguments. """
    args = ["in_toto_keygen.py"]

    with patch.object(sys, 'argv', args + ["bob"]), \
      self.assertRaises(SystemExit):
      in_toto_keygen_main()


  def test_main_optional_args(self):
    """Test CLI command keygen with optional arguments. """
    args = ["in_toto_keygen.py"]
    password = "123456"
    bits = 3072
    with patch.object(sys, 'argv', args + ["-p", "bob"]), \
      patch("getpass.getpass", return_value=password), self.assertRaises(
      SystemExit):
      in_toto_keygen_main()
    with patch.object(sys, 'argv', args + ["-p", "bob", bits]), \
      patch("getpass.getpass", return_value=password), self.assertRaises(
      SystemExit):
      in_toto_keygen_main()


  def test_main_wrong_args(self):
    """Test CLI command with missing arguments. """
    wrong_args_list = [
      ["in_toto_keygen.py"],
      ["in_toto_keygen.py", "-r"]
      ["in_toto_keygen.py", "-p", "bob", "1024"]]

    for wrong_args in wrong_args_list:
      with patch.object(sys, 'argv', wrong_args), self.assertRaises(
        SystemExit):
        in_toto_keygen_main()

  def test_in_toto_keygen_generate_and_write_rsa_keypair(self):
    """in_toto_keygen_generate_and_write_rsa_keypair run through. """
    bits = 3072
    generate_and_write_rsa_keypair("bob", bits)

  def test_in_toto_keygen_prompt_generate_and_write_rsa_keypair(self):
    """in_toto_keygen_prompt_generate_and_write_rsa_keypair run through. """
    name = "bob"
    password = "123456"
    bits = 3072
    with patch("getpass.getpass", return_value=password):
      prompt_generate_and_write_rsa_keypair(name, bits)

  def test_prompt_password(self):
    """Call password prompt. """
    password = "123456"
    with patch("getpass.getpass", return_value=password):
      self.assertEqual(prompt_password(), password)

  def test_create_and_import_encrypted_rsa(self):
    """Create ecrypted RSA key and import private and public key separately."""
    name = "key_encrypted"
    password = "123456"
    bits= 3072
    generate_and_write_rsa_keypair(name, bits, password)
    private_key = import_rsa_key_from_file(name, password)
    public_key = import_rsa_key_from_file(name + ".pub")

    securesystemslib.formats.KEY_SCHEMA.check_match(private_key)
    self.assertTrue(private_key["keyval"].get("private"))
    self.assertTrue(
      securesystemslib.formats.PUBLIC_KEY_SCHEMA.matches(public_key))

  def test_create_and_import_encrypted_rsa_nondefault_length(self):
    name = "key_encrypted_2"
    password = "123456"
    bits = 2048
    generate_and_write_rsa_keypair(name, bits, password)
    private_key = import_rsa_key_from_file(name, password)
    public_key = import_rsa_key_from_file(name + ".pub")

    securesystemslib.formats.KEY_SCHEMA.check_match(private_key)
    self.assertTrue(private_key["keyval"].get("private"))
    self.assertTrue(
      securesystemslib.formats.PUBLIC_KEY_SCHEMA.matches(public_key))

if __name__ == '__main__':
  unittest.main(buffer=True)