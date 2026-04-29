import { useState } from "react";

function AuthScreen({ mode, error, isSubmitting, onModeChange, onSubmit }) {
  const isSignup = mode === "signup";
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const updateField = (event) => {
    setForm((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const submit = (event) => {
    event.preventDefault();
    onSubmit(form);
  };

  return (
    <main className="auth-shell">
      <section className="auth-panel" aria-label={isSignup ? "Sign up" : "Login"}>
        <div className="auth-brand">
          <div className="brand-mark">
            <i className="pi pi-sparkles" aria-hidden="true" />
          </div>
          <div>
            <div className="brand-name">
              Talk2Doc<span>.</span>RAG
            </div>
            <p>Private document chat workspace</p>
          </div>
        </div>

        <div className="auth-copy">
          <p className="eyebrow">{isSignup ? "Create account" : "Welcome back"}</p>
          <h1>{isSignup ? "Start your document workspace." : "Login to your workspace."}</h1>
        </div>

        <form className="auth-form" onSubmit={submit}>
          {isSignup ? (
            <label>
              Name
              <input
                name="name"
                value={form.name}
                onChange={updateField}
                placeholder="Your name"
                required
              />
            </label>
          ) : null}

          <label>
            Email
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={updateField}
              placeholder="you@example.com"
              required
            />
          </label>

          <label>
            Password
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={updateField}
              placeholder={isSignup ? "At least 8 characters" : "Your password"}
              minLength={isSignup ? 8 : 1}
              required
            />
          </label>

          {error ? <p className="auth-error">{error}</p> : null}

          <button className="auth-submit" type="submit" disabled={isSubmitting}>
            <i className={`pi ${isSubmitting ? "pi-spin pi-spinner" : "pi-lock"}`} aria-hidden="true" />
            {isSubmitting ? "Please wait" : isSignup ? "Sign up" : "Login"}
          </button>
        </form>

        <button
          className="auth-switch"
          type="button"
          onClick={() => onModeChange(isSignup ? "login" : "signup")}
        >
          {isSignup ? "Already have an account? Login" : "Need an account? Sign up"}
        </button>
      </section>
    </main>
  );
}

export default AuthScreen;
