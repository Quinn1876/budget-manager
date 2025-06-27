"use client";

import { Account } from "@/types/account";
import { gql, useMutation } from "@apollo/client";
import {
  FormEventHandler,
  HTMLAttributes,
  Ref,
  useCallback,
  useRef,
} from "react";
import SnackBar from "./SnackBar";

interface AccountFormProps {
  account: Account;
  onSubmitSuccess: () => void;
}

const UPDATE_ACCOUNT = gql`
  mutation UpdateAccount(
    $account_number: String!
    $input: UpdateAccountInput!
  ) {
    updateAccount(account_number: $account_number, input: $input) {
      account_type
      owner
      account_name
      initial_balance
    }
  }
`;

interface FormInputProps {
  id: string;
  name?: string;
  label: string;
  defaultValue: HTMLAttributes<HTMLInputElement>["defaultValue"];
  ref?: Ref<HTMLInputElement>;
}

const FormInput = ({ id, name, label, defaultValue, ref }: FormInputProps) => (
  <>
    <label htmlFor={id} className="flex justify-between">
      {label}
    </label>
    <input
      id={id}
      ref={ref}
      name={name ?? id}
      type="text"
      defaultValue={defaultValue}
    />
  </>
);

export default function AccountForm({ account, onSubmitSuccess }: AccountFormProps) {
  const owner = useRef<HTMLInputElement>(null);
  const initialBalance = useRef<HTMLInputElement>(null);
  const accountName = useRef<HTMLInputElement>(null);
  const [updateAccount, { error, called }] = useMutation(UPDATE_ACCOUNT);

  const submitForm = useCallback<FormEventHandler<HTMLFormElement>>(
    (e) => {
      e.preventDefault();
      if (owner.current == null) {
        console.error("Owner not attached");
        return;
      }
      if (initialBalance.current == null) {
        console.error("Initial Balance not attached");
        return;
      }
      if (accountName.current == null) {
        console.error("Account Name not attached");
        return;
      }
      const variables: {account_number: Account["account_number"], input: Partial<Account>} = {
        account_number: account.account_number,
        input: {
        },
      };

      if (initialBalance.current.value) {
        variables.input["initial_balance"] = parseFloat(initialBalance.current.value);
      }

      if (owner.current.value != null) {
        variables.input["owner"] = owner.current.value;
      }

      if (accountName.current.value != null) {
        variables.input["account_name"] = accountName.current.value;
      }

      console.log(variables);
      updateAccount({
        variables
      }).then(() => {
        onSubmitSuccess();
      });
    },
    [account, updateAccount, onSubmitSuccess]
  );

  return (
    <>
        <form onSubmit={submitForm} className="flex flex-col">
        <h1>Account: {account.account_number}</h1>
        <h2>Transaction Sum: {account.balance - account.initial_balance}</h2>

        <FormInput
            label="Account Name"
            id="account_name"
            defaultValue={account.account_name}
            ref={accountName}
            />
        <FormInput
            label="Owner"
            id="owner"
            defaultValue={account.owner}
            ref={owner}
            />
        <FormInput
            label="Initial Balance"
            id="initial_balance"
            defaultValue={account.initial_balance}
            ref={initialBalance}
            />

        <button type="submit" className="self-end">
            Submit
        </button>
        </form>
        <SnackBar
            message="An Error Occurred when submitting the form"
            show={called && error != null}
            variant="error"
            autoHideDurationMs={5000}
        />
    </>
  );
}
