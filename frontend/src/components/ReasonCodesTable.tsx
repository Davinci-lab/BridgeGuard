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
        <section className="card">
            <h2 className="section-title">Reason Code Reference</h2>
            <p className="section-subtitle">Every policy decision is backed by one or more explainable defensive signals.</p>
            {error && <p className="error">{error}</p>}
            <table className="reason-table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {Object.entries(codes).map(([code, desc]) => (
                        <tr key={code}>
                            <td><strong>{code}</strong></td>
                            <td>{desc}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </section>
    );
};

export default ReasonCodesTable;
