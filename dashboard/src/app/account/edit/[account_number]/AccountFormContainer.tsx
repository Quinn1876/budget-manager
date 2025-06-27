"use client"

import AccountForm from "@/components/AccountForm";
import { Account } from "@/types/account";
import { useCallback } from "react";

interface Props {
    account: Account
}

export default function AccountFormContainer({ account } : Props) {
    const onSubmit = useCallback(() => {
        window.history.back();
    }, []);

    return (
        <AccountForm account={account} onSubmitSuccess={onSubmit} />
    )
}
