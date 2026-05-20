import React, { useEffect, useState } from 'react';
import { fetchReasonCodes, getApiErrorMessage } from '../api';

const ReasonCodesTable: React.FC = () => {
    const [codes, setCodes] = useState<Record<string, string>>({});
    const [error, setError] = useState<string>('');

    useEffect(() => {
        fetchReasonCodes()
            .then(res => {
                setCodes(res.data);
                setError('');
            })
            .catch(err => setError(getApiErrorMessage(err)));
    }, []);

    return (
        <section className="space-y-4 rounded-lg border bg-card p-5">
            <h2 className="text-lg font-semibold">Reason Code Reference</h2>
            <p className="text-sm text-muted-foreground">Every policy decision is backed by one or more explainable defensive signals.</p>
            {error && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
            <table className="w-full border-collapse text-sm">
                <thead>
                    <tr className="border-b">
                        <th className="px-3 py-2 text-left text-xs font-semibold uppercase text-muted-foreground">Code</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold uppercase text-muted-foreground">Description</th>
                    </tr>
                </thead>
                <tbody>
                    {Object.entries(codes).map(([code, desc]) => (
                        <tr className="border-b last:border-0" key={code}>
                            <td className="px-3 py-2 align-top"><strong>{code}</strong></td>
                            <td className="px-3 py-2 text-muted-foreground">{desc}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </section>
    );
};

export default ReasonCodesTable;
