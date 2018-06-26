# AWS setup
provider "aws" {
  region                  = "us-east-1"
  shared_credentials_file = "/Users/spencer/.aws/credentials"
  profile                 = "terraform"
}

resource "aws_instance" "terraform_tutorial_new" {
  ami           = "ami-b374d5a5"
  instance_type = "t2.micro"

  tags {
    Name = "spencers cool machine"
  }
}

resource "aws_eip" "ip" {
  instance = "${aws_instance.terraform_tutorial_new.id}"
}
